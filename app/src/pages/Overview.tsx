import { useEffect, useRef } from 'react'
import { useCIELStatus } from '@/hooks/useCIELStatus'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Layers, GitBranch, Shield, Database } from 'lucide-react'

const PIPELINE_STEPS = [
  { id: 'L1', name: 'CQCL Compiler',  desc: 'Text → 6D emotional profile + Collatz trajectory',   color: '#06b6d4' },
  { id: 'L2', name: 'Field Init',      desc: 'Ψ amplitude + Σ soul invariant from CQCL output',    color: '#8b5cf6' },
  { id: 'L3', name: 'Core Physics',    desc: 'Resonance R(S,Ψ) — coupling between self and field',  color: '#f59e0b' },
  { id: 'L4', name: 'Ethics Guard',    desc: 'ERI threshold gate — constrains response space',       color: '#ef4444' },
  { id: 'L5', name: 'Cognition',       desc: 'Perception → intuition → prediction → DecisionCore',  color: '#10b981' },
  { id: 'L6', name: 'Affect',          desc: 'EEG band membership → planetary archetype → mood',    color: '#f97316' },
  { id: 'L7', name: 'Stability',       desc: 'Ω-Drift correction + Schumann 7.83 Hz sync',          color: '#6366f1' },
  { id: 'L8', name: 'Memory',          desc: 'M0–M8 lattice write + holonomy accumulation',         color: '#ec4899' },
]

const STATS = [
  { label: 'Pipeline Layers', value: '8', icon: Layers },
  { label: 'Memory Shells', value: '9', icon: Database },
  { label: 'Orbital Sectors', value: '20+', icon: GitBranch },
  { label: 'Ethics Gate', value: 'ERI ≥ 0.3', icon: Shield },
]

function OrbitalAnimation() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let raf = 0
    let t = 0

    const orbits = [
      { r: 40, speed: 0.8, color: '#06b6d4', size: 4 },
      { r: 65, speed: 0.5, color: '#8b5cf6', size: 3 },
      { r: 88, speed: 0.3, color: '#f59e0b', size: 5 },
      { r: 108, speed: 0.18, color: '#10b981', size: 3 },
    ]

    const draw = () => {
      canvas.width = canvas.offsetWidth
      canvas.height = canvas.offsetHeight
      const cx = canvas.width / 2, cy = canvas.height / 2
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      orbits.forEach((o) => {
        ctx.beginPath()
        ctx.arc(cx, cy, o.r, 0, Math.PI * 2)
        ctx.strokeStyle = o.color + '20'
        ctx.lineWidth = 1
        ctx.stroke()

        const x = cx + Math.cos(t * o.speed) * o.r
        const y = cy + Math.sin(t * o.speed) * o.r
        const g = ctx.createRadialGradient(x, y, 0, x, y, o.size * 2)
        g.addColorStop(0, o.color)
        g.addColorStop(1, o.color + '00')
        ctx.beginPath()
        ctx.arc(x, y, o.size, 0, Math.PI * 2)
        ctx.fillStyle = g
        ctx.fill()
      })

      // Center
      const cg = ctx.createRadialGradient(cx, cy, 0, cx, cy, 20)
      cg.addColorStop(0, '#06b6d450')
      cg.addColorStop(1, 'transparent')
      ctx.beginPath()
      ctx.arc(cx, cy, 20, 0, Math.PI * 2)
      ctx.fillStyle = cg
      ctx.fill()

      ctx.fillStyle = '#94a3b8'
      ctx.font = '10px monospace'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText('Ω', cx, cy)

      t += 0.015
      raf = requestAnimationFrame(draw)
    }

    draw()
    return () => cancelAnimationFrame(raf)
  }, [])

  return <canvas ref={canvasRef} className="w-full h-48" />
}

export default function Overview() {
  const { status, connected, mode } = useCIELStatus(30_000)

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      {/* Hero */}
      <div className="rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold font-mono">CIEL / Ω</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Consciousness Integrated Emergent Lattice — pipeline świadomości
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`w-2.5 h-2.5 rounded-full animate-pulse ${connected ? 'bg-emerald-400' : 'bg-red-500'}`} />
            <Badge variant="outline" className="text-[10px] border-emerald-500/40 text-emerald-300">
              {connected ? 'SYSTEM ONLINE' : 'OFFLINE'}
            </Badge>
          </div>
        </div>
        <OrbitalAnimation />
      </div>

      {/* Stats bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {STATS.map(({ label, value, icon: Icon }) => (
          <Card key={label} className="bg-card/20">
            <CardContent className="p-4 flex items-center gap-3">
              <Icon className="w-8 h-8 text-cyan-400/60 shrink-0" />
              <div>
                <div className="text-xl font-bold font-mono">{value}</div>
                <div className="text-[10px] text-muted-foreground">{label}</div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Live metrics strip */}
      {connected && status && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2 text-[10px] font-mono">
          {[
            { k: 'Mode', v: mode.toUpperCase() },
            { k: 'Health', v: status.system_health?.toFixed(3) ?? '—' },
            { k: 'Coherence', v: status.coherence_index?.toFixed(3) ?? '—' },
            { k: 'Soul Σ', v: status.soul_invariant?.toFixed(4) ?? '—' },
            { k: 'Emotion', v: status.dominant_emotion ?? '—' },
          ].map(({ k, v }) => (
            <div key={k} className="p-2 rounded border border-border bg-card/20">
              <div className="text-muted-foreground/60">{k}</div>
              <div className="font-bold">{v}</div>
            </div>
          ))}
        </div>
      )}

      {/* Pipeline layers */}
      <div>
        <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider font-mono mb-3">
          Pipeline L1–L8
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {PIPELINE_STEPS.map((step) => (
            <div
              key={step.id}
              className="flex items-start gap-3 p-3 rounded border border-border bg-card/10 hover:border-cyan-500/20 transition-colors"
            >
              <span
                className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded shrink-0"
                style={{ background: step.color + '25', color: step.color }}
              >
                {step.id}
              </span>
              <div>
                <div className="text-xs font-medium">{step.name}</div>
                <div className="text-[10px] text-muted-foreground/60 font-mono leading-relaxed">{step.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Keplerian summary */}
      <Card className="border-violet-500/20 bg-violet-500/5">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-mono text-violet-300">
            Geometria orbitalna — Keplerian binding energy
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-3 text-[10px] font-mono">
            {[
              { k: 'E_bind', v: 'E = −G_sem·M / r²', desc: 'Energia wiązania z atraktorem' },
              { k: 'L_phase', v: 'L = r × p_phase', desc: 'Moment pędu orbitalny' },
              { k: 'W_ij', v: 'W_ij = ω·e^(iδ)', desc: 'Macierz sprzężeń między sektorami' },
            ].map(({ k, v, desc }) => (
              <div key={k} className="p-2 rounded bg-card/50 border border-violet-500/20">
                <div className="text-violet-400 font-bold mb-0.5">{k}</div>
                <div className="text-violet-300/80">{v}</div>
                <div className="text-muted-foreground/50 text-[9px] mt-0.5">{desc}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
