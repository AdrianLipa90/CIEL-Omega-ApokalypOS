import { useState, useEffect, useMemo } from 'react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { getCIELBase } from '@/lib/cielApi'

// ── Kepler constants (mirror of orbital_shell.py) ──────────────────────
const G_SEM = 0.42
const M_ATTRACTOR = 1.0

function computeEBind(rPhase: number): number {
  const r = Math.max(rPhase, 1e-6)
  return -G_SEM * M_ATTRACTOR / (r * r)
}

function computeAngularMomentum(rPhase: number, phi: number): number {
  // p_phase ≈ amplitude * phi — phase momentum proxy
  const pPhase = phi % (Math.PI * 2)
  return rPhase * pPhase
}

function shellFromEBind(eBind: number): number {
  // Deeper binding → inner shell (M0)
  const thresholds = [-500, -100, -20, -5, -1.5, -0.5, -0.15, -0.05]
  for (let i = 0; i < thresholds.length; i++) {
    if (eBind < thresholds[i]) return i
  }
  return 8
}

const SHELL_NAMES: Record<number, string> = {
  0: 'K (M0)', 1: 'L (M1)', 2: 'M (M2)', 3: 'N (M3)',
  4: 'O (M4)', 5: 'P (M5)', 6: 'Q (M6)', 7: 'R (M7)', 8: 'S (M8)',
}

const ORB_TYPE_COLOR: Record<string, string> = {
  S: '#6366f1', P: '#22d3ee', D: '#f59e0b', F: '#10b981',
  R: '#f43f5e', G: '#a855f7',
}

interface OrbNode {
  id: string
  label: string
  theta: number
  phi: number
  amplitude: number
  coherence_weight: number
  info_mass: number
  orbital_type: string
  is_attractor: boolean
  // computed
  rPhase: number
  eBind: number
  lPhase: number
  shell: number
}

interface OrbEdge {
  src: string
  dst: string
  w: number
}

interface GeomData {
  nodes: OrbNode[]
  edges: OrbEdge[]
}

// ── Phase-Plane SVG ─────────────────────────────────────────────────────
function PhasePlane({ nodes, edges }: { nodes: OrbNode[]; edges: OrbEdge[] }) {
  const W = 480, H = 480, cx = W / 2, cy = H / 2

  const nodeMap = useMemo(() => {
    const m: Record<string, OrbNode> = {}
    nodes.forEach((n) => (m[n.id] = n))
    return m
  }, [nodes])

  // Project onto Bloch sphere equatorial plane: x = sin(θ)cos(φ), y = sin(θ)sin(φ)
  const project = (n: OrbNode, scale: number) => ({
    x: cx + Math.sin(n.theta) * Math.cos(n.phi) * scale,
    y: cy + Math.sin(n.theta) * Math.sin(n.phi) * scale,
  })

  const scale = (W / 2) * 0.88

  // Shell rings
  const shells = [0.1, 0.25, 0.45, 0.62, 0.78, 0.9]

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full max-w-lg mx-auto select-none">
      <defs>
        <filter id="wijGlow">
          <feGaussianBlur stdDeviation="1.5" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>

      {/* Bloch sphere projection circles */}
      <circle cx={cx} cy={cy} r={scale} fill="none" stroke="#1e293b" strokeWidth="1" />
      {shells.map((s, i) => (
        <circle key={i} cx={cx} cy={cy} r={scale * s}
          fill="none" stroke="#0f172a" strokeWidth="0.5" strokeDasharray="2 4" />
      ))}
      <text x={cx} y={cy + scale + 14} fill="#334155" fontSize="7"
        textAnchor="middle" fontFamily="mono">Bloch sphere — equatorial projection</text>

      {/* W_ij edges (coupling threads) */}
      {edges
        .filter((e) => e.w > 0.15)
        .map((e, i) => {
          const a = nodeMap[e.src], b = nodeMap[e.dst]
          if (!a || !b) return null
          const pa = project(a, scale), pb = project(b, scale)
          const opacity = Math.min(0.85, e.w * 1.2)
          const strokeW = e.w > 0.5 ? 1.5 : e.w > 0.3 ? 0.8 : 0.4
          return (
            <line key={i} x1={pa.x} y1={pa.y} x2={pb.x} y2={pb.y}
              stroke="#38bdf8" strokeWidth={strokeW} opacity={opacity} />
          )
        })}

      {/* Nodes */}
      {nodes.map((n) => {
        const p = project(n, scale)
        const col = ORB_TYPE_COLOR[n.orbital_type] ?? '#64748b'
        const r = 3 + n.amplitude * 5
        return (
          <g key={n.id}>
            <circle cx={p.x} cy={p.y} r={r + 3} fill={col} opacity="0.08" />
            <circle cx={p.x} cy={p.y} r={r} fill={col} opacity={n.is_attractor ? 1 : 0.75}
              filter={n.is_attractor ? 'url(#wijGlow)' : undefined} />
            <text x={p.x} y={p.y - r - 3} fill="#94a3b8" fontSize="7"
              fontFamily="mono" textAnchor="middle">
              {n.label.slice(0, 10)}
            </text>
          </g>
        )
      })}

      {/* Attractor label */}
      {nodes.filter((n) => n.is_attractor).map((n) => {
        const p = project(n, scale)
        return (
          <text key={n.id + '_label'} x={p.x} y={p.y + 3}
            fill="#f8fafc" fontSize="6" fontFamily="mono" textAnchor="middle" fontWeight="bold">
            Ω
          </text>
        )
      })}
    </svg>
  )
}

// ── Sector table ────────────────────────────────────────────────────────
function SectorTable({ nodes }: { nodes: OrbNode[] }) {
  const sorted = [...nodes].sort((a, b) => a.eBind - b.eBind)
  return (
    <ScrollArea className="h-80">
      <table className="w-full text-[10px] font-mono">
        <thead>
          <tr className="text-muted-foreground/60 border-b border-border">
            <th className="text-left py-1 pr-2">Sektor</th>
            <th className="text-right pr-2">Typ</th>
            <th className="text-right pr-2">ρ</th>
            <th className="text-right pr-2">E_bind</th>
            <th className="text-right pr-2">L_phase</th>
            <th className="text-right pr-2">Shell</th>
            <th className="text-right">Amp</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((n) => (
            <tr key={n.id} className="border-b border-border/30 hover:bg-card/50">
              <td className="py-1 pr-2 truncate max-w-[100px]">{n.label}</td>
              <td className="text-right pr-2">
                <span style={{ color: ORB_TYPE_COLOR[n.orbital_type] ?? '#64748b' }}>
                  {n.orbital_type}
                </span>
              </td>
              <td className="text-right pr-2">{n.rPhase.toFixed(3)}</td>
              <td className="text-right pr-2 text-amber-400">{n.eBind.toFixed(2)}</td>
              <td className="text-right pr-2 text-violet-400">{n.lPhase.toFixed(3)}</td>
              <td className="text-right pr-2 text-cyan-400">{SHELL_NAMES[n.shell]}</td>
              <td className="text-right">{n.amplitude.toFixed(3)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </ScrollArea>
  )
}

// ── Euler-Berry summary ─────────────────────────────────────────────────
function EulerBerrySummary({ nodes, edges }: { nodes: OrbNode[]; edges: OrbEdge[] }) {
  if (nodes.length === 0) return null

  const meanPhi = nodes.reduce((s, n) => s + n.phi, 0) / nodes.length
  const meanTheta = nodes.reduce((s, n) => s + n.theta, 0) / nodes.length
  const meanEBind = nodes.reduce((s, n) => s + n.eBind, 0) / nodes.length
  const totalLPhase = nodes.reduce((s, n) => s + Math.abs(n.lPhase), 0)
  const meanCoh = nodes.reduce((s, n) => s + n.coherence_weight, 0) / nodes.length
  const totalMass = nodes.reduce((s, n) => s + n.info_mass, 0)
  const strongEdges = edges.filter((e) => e.w > 0.5).length
  const winding = Math.round(meanPhi / (Math.PI * 2) * nodes.length) % 20

  const metrics = [
    { label: 'Mean φ (rad)', value: meanPhi.toFixed(4) },
    { label: 'Mean θ (rad)', value: meanTheta.toFixed(4) },
    { label: 'Mean E_bind', value: meanEBind.toFixed(3) },
    { label: 'Σ |L_phase|', value: totalLPhase.toFixed(3) },
    { label: 'Mean coherence', value: meanCoh.toFixed(4) },
    { label: 'Total info_mass', value: totalMass.toFixed(3) },
    { label: 'Strong W_ij (>0.5)', value: String(strongEdges) },
    { label: 'Winding est.', value: String(winding) },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
      {metrics.map(({ label, value }) => (
        <div key={label} className="p-2 rounded border border-border bg-card/30 text-[10px] font-mono">
          <div className="text-muted-foreground/60">{label}</div>
          <div className="font-bold text-sm">{value}</div>
        </div>
      ))}
    </div>
  )
}

// ── W_ij matrix heatmap (top connections) ──────────────────────────────
function WijHeatmap({ edges }: { edges: OrbEdge[] }) {
  const top = [...edges].sort((a, b) => b.w - a.w).slice(0, 24)
  return (
    <ScrollArea className="h-48">
      <div className="space-y-1">
        {top.map((e, i) => (
          <div key={i} className="flex items-center gap-2 text-[9px] font-mono">
            <span className="text-muted-foreground/70 w-4 shrink-0">{i + 1}</span>
            <span className="text-cyan-300 truncate w-28">{e.src.replace('ent_', '')}</span>
            <span className="text-muted-foreground/40">⟶</span>
            <span className="text-violet-300 truncate w-28">{e.dst.replace('ent_', '')}</span>
            <div className="flex-1 h-1.5 rounded bg-card overflow-hidden">
              <div
                className="h-full rounded bg-cyan-500"
                style={{ width: `${Math.min(100, e.w * 100)}%` }}
              />
            </div>
            <span className="text-muted-foreground w-10 text-right">{e.w.toFixed(3)}</span>
          </div>
        ))}
      </div>
    </ScrollArea>
  )
}

export default function Orbital() {
  const [data, setData] = useState<GeomData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    ;(async () => {
      const base = await getCIELBase()
      const raw: { nodes: OrbNode[]; edges: OrbEdge[]; error?: string } = await fetch(
        `${base}/api/geometry/sectors`,
      ).then((r) => r.json())

      if (raw.error) {
        setError(raw.error)
        setData({ nodes: [], edges: [] })
        return
      }
      // Compute Kepler quantities for each node
      const nodes: OrbNode[] = raw.nodes.map((n) => {
        const rPhase = Math.sqrt(
          Math.sin(n.theta) * Math.sin(n.theta) + (1 - Math.cos(n.theta)) * (1 - Math.cos(n.theta)) * 0.5,
        )
        const eBind = computeEBind(rPhase)
        const lPhase = computeAngularMomentum(rPhase, n.phi)
        return { ...n, rPhase, eBind, lPhase, shell: shellFromEBind(eBind) }
      })
      setData({ nodes, edges: raw.edges })
    })()
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false))
  }, [])

  if (loading)
    return <div className="text-sm text-muted-foreground py-16 text-center">Ładowanie geometrii…</div>

  const nodes = data?.nodes ?? []
  const edges = data?.edges ?? []

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Orbital</h1>
        <p className="text-sm text-muted-foreground">
          Dynamika Keplera · sfera Blocha · W_ij nici sprzężeń · E_bind = −G_sem M / r²
        </p>
      </div>

      {error && (
        <div className="p-3 rounded border border-red-500/30 bg-red-500/10 text-xs font-mono text-red-300">
          Backend error: {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Phase plane */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-mono flex items-center gap-2">
              Bloch Sphere — Projekcja ekwatorialna
              <Badge variant="outline" className="text-[9px]">{nodes.length} węzłów</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <PhasePlane nodes={nodes} edges={edges} />
            <div className="flex flex-wrap gap-2 mt-3 text-[9px] font-mono justify-center">
              {Object.entries(ORB_TYPE_COLOR).map(([t, c]) => (
                <span key={t} className="flex items-center gap-1">
                  <span style={{ background: c }} className="w-2 h-2 rounded-full inline-block" />
                  {t}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Euler-Berry + W_ij */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-mono">Euler-Berry — metryki orbitalne</CardTitle>
            </CardHeader>
            <CardContent>
              <EulerBerrySummary nodes={nodes} edges={edges} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-mono">
                W_ij — nici sprzężeń
                <span className="ml-2 text-[9px] text-muted-foreground font-normal">
                  top {Math.min(24, edges.length)} z {edges.length}
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <WijHeatmap edges={edges} />
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Sector table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-mono">
            Tabela sektorów — Kepler E_bind · L_phase · Shell
          </CardTitle>
        </CardHeader>
        <CardContent>
          <SectorTable nodes={nodes} />
        </CardContent>
      </Card>
    </div>
  )
}
