import { useState, useEffect, useMemo, type ReactElement } from 'react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { getCIELBase } from '@/lib/cielApi'

// Kepler helpers (same constants as orbital_shell.py)
const G_SEM = 0.42
const M_ATTRACTOR = 1.0

function computeEBind(rho: number): number {
  const r = Math.max(rho, 1e-6)
  return -G_SEM * M_ATTRACTOR / (r * r)
}

function computeLPhase(rho: number, phi: number): number {
  return rho * (phi % (Math.PI * 2))
}

interface HolonomicSite {
  id: string
  label: string
  phi: number
  rho: number
  theta: number
  berry_phase: number
  info_mass: number
  orbital_type: string
  is_attractor: boolean
  // computed
  eBind: number
  lPhase: number
  // W_ij
  connections: { target: string; w: number }[]
}

const ORB_COLORS: Record<string, string> = {
  S: '#6366f1', P: '#22d3ee', D: '#f59e0b', F: '#10b981',
  R: '#f43f5e', G: '#a855f7',
}

// Poincaré disk with holonomic sites
function HolonomicDisk({ sites }: { sites: HolonomicSite[] }) {
  const W = 400, H = 400, cx = W / 2, cy = H / 2, R = 180

  const project = (site: HolonomicSite) => {
    const rho = Math.min(0.96, site.rho > 0 ? site.rho : 0.05 + site.info_mass * 0.2)
    const x = cx + Math.cos(site.phi) * R * rho
    const y = cy + Math.sin(site.phi) * R * rho
    return { x, y }
  }

  // Draw W_ij edges
  const edges = useMemo(() => {
    const lines: ReactElement[] = []
    sites.forEach((s) => {
      const pa = project(s)
      s.connections.forEach((c, ci) => {
        if (c.w < 0.2) return
        const b = sites.find((x) => x.id === c.target)
        if (!b) return
        const pb = project(b)
        lines.push(
          <line key={`${s.id}-${c.target}-${ci}`}
            x1={pa.x} y1={pa.y} x2={pb.x} y2={pb.y}
            stroke="#38bdf8" strokeWidth={c.w > 0.5 ? 1 : 0.4}
            opacity={Math.min(0.7, c.w)} />,
        )
      })
    })
    return lines
  }, [sites])

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full max-w-sm mx-auto select-none">
      <circle cx={cx} cy={cy} r={R} fill="none" stroke="#1e293b" strokeWidth="1.5" />
      <circle cx={cx} cy={cy} r={R * 0.66} fill="none" stroke="#0f172a" strokeWidth="0.5" strokeDasharray="2 3" />
      <circle cx={cx} cy={cy} r={R * 0.33} fill="none" stroke="#0f172a" strokeWidth="0.5" strokeDasharray="2 3" />

      {edges}

      {sites.map((s) => {
        const { x, y } = project(s)
        const col = ORB_COLORS[s.orbital_type] ?? '#64748b'
        const r = s.is_attractor ? 10 : 3 + s.info_mass * 5
        return (
          <g key={s.id}>
            <circle cx={x} cy={y} r={r + 3} fill={col} opacity="0.06" />
            <circle cx={x} cy={y} r={r} fill={col} opacity={s.is_attractor ? 1 : 0.75} />
            <text x={x} y={y - r - 3} fill="#94a3b8" fontSize="7" fontFamily="mono" textAnchor="middle">
              {s.label.slice(0, 8)}
            </text>
          </g>
        )
      })}
      <text x={cx} y={cy} fill="#94a3b8" fontSize="8" fontFamily="mono" textAnchor="middle" dominantBaseline="middle">
        Ω
      </text>
      <text x={cx} y={H - 8} fill="#334155" fontSize="7" fontFamily="mono" textAnchor="middle">
        Holonomic sites · Poincaré disk
      </text>
    </svg>
  )
}

// Site card with full Kepler + W_ij info
function SiteCard({ site }: { site: HolonomicSite }) {
  const col = ORB_COLORS[site.orbital_type] ?? '#64748b'

  return (
    <Card className="bg-card/20 hover:border-cyan-500/30 transition-colors">
      <CardContent className="p-3">
        <div className="flex items-start justify-between gap-2 mb-2">
          <div>
            <div className="text-sm font-semibold font-mono truncate">{site.label}</div>
            <div className="text-[9px] text-muted-foreground/60 font-mono truncate">{site.id}</div>
          </div>
          <div className="flex flex-col items-end gap-1 shrink-0">
            <span
              style={{ background: col + '33', color: col, borderColor: col + '66' }}
              className="text-[9px] px-1.5 py-0.5 rounded border font-mono font-bold"
            >
              {site.orbital_type}
            </span>
            {site.is_attractor && (
              <Badge variant="outline" className="text-[8px] border-amber-500/40 text-amber-300">ATTRACTOR</Badge>
            )}
          </div>
        </div>

        {/* Orbital coordinates */}
        <div className="grid grid-cols-3 gap-1 text-[9px] font-mono mb-2">
          {[
            { k: 'φ (rad)', v: site.phi.toFixed(3) },
            { k: 'ρ', v: site.rho.toFixed(4) },
            { k: 'θ', v: site.theta.toFixed(4) },
            { k: 'E_bind', v: site.eBind.toFixed(2) },
            { k: 'L_phase', v: site.lPhase.toFixed(3) },
            { k: 'Berry φ', v: site.berry_phase.toFixed(4) },
          ].map(({ k, v }) => (
            <div key={k} className="p-1 rounded bg-card/50 border border-border/40">
              <div className="text-muted-foreground/60">{k}</div>
              <div className="font-bold">{v}</div>
            </div>
          ))}
        </div>

        {/* W_ij connections */}
        {site.connections.length > 0 && (
          <div className="space-y-0.5">
            <div className="text-[8px] text-muted-foreground/50 font-mono">W_ij nici</div>
            {site.connections.slice(0, 3).map((c, i) => (
              <div key={i} className="flex items-center gap-1 text-[8px] font-mono">
                <span className="text-cyan-400/60 truncate w-20">{c.target.replace('ent_', '')}</span>
                <div className="flex-1 h-1 rounded bg-card">
                  <div className="h-full rounded bg-cyan-500" style={{ width: `${Math.min(100, c.w * 100)}%` }} />
                </div>
                <span className="text-muted-foreground w-8 text-right">{c.w.toFixed(2)}</span>
              </div>
            ))}
            {site.connections.length > 3 && (
              <div className="text-[8px] text-muted-foreground/40 font-mono">+{site.connections.length - 3} więcej</div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default function Sites() {
  const [sites, setSites] = useState<HolonomicSite[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [sortBy, setSortBy] = useState<'phi' | 'rho' | 'eBind' | 'info_mass'>('eBind')

  useEffect(() => {
    ;(async () => {
      const base = await getCIELBase()
      const raw: { nodes: any[]; edges: any[]; error?: string } = await fetch(`${base}/api/geometry/sectors`).then(
        (r) => r.json(),
      )
      if (raw.error) {
        setError(raw.error)
        return
      }

      // Build adjacency list for W_ij
      const adj: Record<string, { target: string; w: number }[]> = {}
      ;(raw.edges ?? []).forEach((e: any) => {
        if (!adj[e.src]) adj[e.src] = []
        adj[e.src].push({ target: e.dst, w: e.w })
      })

      const s: HolonomicSite[] = (raw.nodes ?? []).map((n: any) => {
        const rho = n.rho ?? Math.sin(n.theta ?? 0)
        const phi = n.phi ?? 0
        return {
          id: n.id,
          label: n.label ?? n.id.replace('ent_', '').replace(/_/g, ' '),
          phi,
          rho,
          theta: n.theta ?? 0,
          berry_phase: n.berry_phase ?? 0,
          info_mass: n.info_mass ?? 0.4,
          orbital_type: n.orbital_type ?? 'R',
          is_attractor: !!n.is_attractor,
          eBind: computeEBind(rho),
          lPhase: computeLPhase(rho, phi),
          connections: adj[n.id] ?? [],
        }
      })
      setSites(s)
    })()
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false))
  }, [])

  const sorted = useMemo(() => {
    return [...sites].sort((a, b) => {
      if (sortBy === 'eBind') return a.eBind - b.eBind
      if (sortBy === 'phi') return a.phi - b.phi
      if (sortBy === 'rho') return a.rho - b.rho
      return b.info_mass - a.info_mass
    })
  }, [sites, sortBy])

  // Summary stats
  const totalMass = sites.reduce((s, n) => s + n.info_mass, 0)
  const meanEBind = sites.length ? sites.reduce((s, n) => s + n.eBind, 0) / sites.length : 0
  const totalEdges = sites.reduce((s, n) => s + n.connections.length, 0)
  const attractors = sites.filter((n) => n.is_attractor)

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Sites</h1>
        <p className="text-sm text-muted-foreground">
          Holonomiczne węzły pamięci — lokalizacja fazowa · E_bind Keplera · nici W_ij
        </p>
      </div>

      {error && (
        <div className="p-3 rounded border border-red-500/30 bg-red-500/10 text-xs font-mono text-red-300">
          {error}
        </div>
      )}

      {/* Summary row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: 'Węzłów', value: String(sites.length) },
          { label: 'Atraktorów', value: String(attractors.length) },
          { label: 'Σ info_mass', value: totalMass.toFixed(3) },
          { label: 'Mean E_bind', value: meanEBind.toFixed(2) },
        ].map(({ label, value }) => (
          <div key={label} className="p-3 rounded border border-border bg-card/20 text-[11px] font-mono">
            <div className="text-muted-foreground/60">{label}</div>
            <div className="font-bold text-base">{value}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Holonomic disk */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-mono">
              Poincaré disk — holonomic sites
              <span className="ml-2 text-[9px] text-muted-foreground font-normal">
                {totalEdges} W_ij krawędzi
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-sm text-muted-foreground py-8 text-center">Ładowanie…</div>
            ) : (
              <HolonomicDisk sites={sites} />
            )}
          </CardContent>
        </Card>

        {/* Site list */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-[10px] font-mono text-muted-foreground">Sortuj:</span>
            {(['eBind', 'phi', 'rho', 'info_mass'] as const).map((k) => (
              <button
                key={k}
                onClick={() => setSortBy(k)}
                className={`px-2 py-0.5 text-[10px] font-mono rounded border transition-colors ${
                  sortBy === k
                    ? 'border-cyan-500/40 bg-cyan-500/10 text-cyan-300'
                    : 'border-border text-muted-foreground'
                }`}
              >
                {k}
              </button>
            ))}
          </div>
          <ScrollArea className="h-[420px]">
            <div className="space-y-2 pr-1">
              {sorted.map((site) => (
                <SiteCard key={site.id} site={site} />
              ))}
            </div>
          </ScrollArea>
        </div>
      </div>
    </div>
  )
}
