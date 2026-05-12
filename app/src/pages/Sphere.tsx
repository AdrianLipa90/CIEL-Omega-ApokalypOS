import { useEffect, useRef } from 'react'
import { useCIELStatus } from '@/hooks/useCIELStatus'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

// Bloch sphere SVG projection — theta/phi → 3D → 2D
function BlochSphereCanvas({
  theta,
  phi,
  soul,
  mode,
}: {
  theta: number
  phi: number
  soul: number
  mode: string
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const W = canvas.offsetWidth
    const H = canvas.offsetHeight
    canvas.width = W
    canvas.height = H
    const cx = W / 2, cy = H / 2
    const R = Math.min(W, H) * 0.42

    ctx.clearRect(0, 0, W, H)

    // Sphere outline
    ctx.beginPath()
    ctx.arc(cx, cy, R, 0, Math.PI * 2)
    ctx.strokeStyle = '#1e293b'
    ctx.lineWidth = 1.5
    ctx.stroke()

    // Equator ellipse
    ctx.beginPath()
    ctx.ellipse(cx, cy, R, R * 0.28, 0, 0, Math.PI * 2)
    ctx.strokeStyle = '#1e293b'
    ctx.lineWidth = 0.8
    ctx.stroke()

    // Axis lines
    ctx.setLineDash([3, 4])
    ctx.strokeStyle = '#334155'
    ctx.lineWidth = 0.8
    ctx.beginPath(); ctx.moveTo(cx, cy - R - 10); ctx.lineTo(cx, cy + R + 10); ctx.stroke()
    ctx.beginPath(); ctx.moveTo(cx - R - 10, cy); ctx.lineTo(cx + R + 10, cy); ctx.stroke()
    ctx.setLineDash([])

    // Poles
    ctx.fillStyle = '#475569'
    ctx.font = '10px monospace'
    ctx.textAlign = 'center'
    ctx.fillText('|0⟩', cx, cy - R - 14)
    ctx.fillText('|1⟩', cx, cy + R + 18)
    ctx.fillText('+X', cx + R + 14, cy + 4)
    ctx.fillText('+Y', cx - R - 14, cy + 4)

    // Ψ state point
    const sinT = Math.sin(theta)
    const cosT = Math.cos(theta)
    const cosP = Math.cos(phi)
    const sinP = Math.sin(phi)

    // 3D → isometric 2D projection (simplified orthographic)
    const x3 = sinT * cosP
    const y3 = sinT * sinP
    const z3 = cosT

    // Project onto 2D: x = x3 * R (with y3 foreshortened), y = -z3 * R
    const px = cx + (x3 - y3 * 0.4) * R
    const py = cy - z3 * R

    // Draw trajectory arc
    ctx.beginPath()
    for (let a = 0; a <= theta; a += 0.05) {
      const sx = cx + (Math.sin(a) * Math.cos(phi) - Math.sin(a) * Math.sin(phi) * 0.4) * R
      const sy = cy - Math.cos(a) * R
      if (a === 0) ctx.moveTo(cx, cy - R)
      else ctx.lineTo(sx, sy)
    }
    ctx.strokeStyle = '#06b6d440'
    ctx.lineWidth = 1.5
    ctx.stroke()

    // Center → Ψ line
    ctx.beginPath()
    ctx.moveTo(cx, cy)
    ctx.lineTo(px, py)
    ctx.strokeStyle = '#06b6d4'
    ctx.lineWidth = 1.5
    ctx.setLineDash([2, 3])
    ctx.stroke()
    ctx.setLineDash([])

    // Ψ point
    const modeColor = mode === 'deep' ? '#10b981' : mode === 'safe' ? '#ef4444' : '#f59e0b'
    const rp = 5 + soul * 6
    const grd = ctx.createRadialGradient(px, py, 0, px, py, rp * 2)
    grd.addColorStop(0, modeColor)
    grd.addColorStop(1, modeColor + '00')
    ctx.beginPath()
    ctx.arc(px, py, rp * 1.8, 0, Math.PI * 2)
    ctx.fillStyle = grd
    ctx.fill()

    ctx.beginPath()
    ctx.arc(px, py, rp, 0, Math.PI * 2)
    ctx.fillStyle = modeColor
    ctx.fill()

    // Label
    ctx.fillStyle = '#94a3b8'
    ctx.font = '9px monospace'
    ctx.textAlign = 'left'
    ctx.fillText(`|Ψ⟩`, px + rp + 4, py + 3)

    // Soul invariant ring
    const ringR = R * 0.92
    ctx.beginPath()
    ctx.arc(cx, cy, ringR, -Math.PI / 2, -Math.PI / 2 + soul * Math.PI * 2)
    ctx.strokeStyle = '#a855f780'
    ctx.lineWidth = 3
    ctx.stroke()

  }, [theta, phi, soul, mode])

  return <canvas ref={canvasRef} className="w-full aspect-square" />
}

export default function Sphere() {
  const { status, mode } = useCIELStatus(5000)

  const theta = (status?.closure_penalty ?? 5) % (Math.PI * 2)
  const phi = ((status?.soul_invariant ?? 0) * Math.PI * 8) % (Math.PI * 2)
  const soul = Math.min(1, (status?.soul_invariant ?? 0) * 2)

  const modeStyle = {
    deep: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
    standard: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    safe: 'bg-red-500/20 text-red-300 border-red-500/30',
  }[mode] ?? 'bg-amber-500/20 text-amber-300 border-amber-500/30'

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Sphere</h1>
        <p className="text-sm text-muted-foreground">
          Sfera Blocha — stan kwantowy |Ψ⟩ · tożsamość w przestrzeni Hilberta · holonomia Berry'ego
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-mono flex items-center justify-between">
              Bloch Sphere — |Ψ⟩ live
              <Badge variant="outline" className={`text-[9px] ${modeStyle}`}>
                {mode.toUpperCase()}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <BlochSphereCanvas theta={theta} phi={phi} soul={soul} mode={mode} />
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-mono">Koordinaty orbitalnte</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
                {[
                  { k: 'θ (polar)', v: theta.toFixed(5) },
                  { k: 'φ (azimuth)', v: phi.toFixed(5) },
                  { k: 'sin(θ)', v: Math.sin(theta).toFixed(5) },
                  { k: 'cos(θ)', v: Math.cos(theta).toFixed(5) },
                  { k: 'Soul Σ', v: soul.toFixed(6) },
                  { k: 'Closure', v: (status?.closure_penalty ?? 0).toFixed(4) },
                  { k: 'Coherence', v: (status?.coherence_index ?? 0).toFixed(5) },
                  { k: 'Health', v: (status?.system_health ?? 0).toFixed(5) },
                ].map(({ k, v }) => (
                  <div key={k} className="p-2 rounded border border-border bg-card/20">
                    <div className="text-muted-foreground/60">{k}</div>
                    <div className="font-bold">{v}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="border-violet-500/20 bg-violet-500/5">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-mono text-violet-300">Soul Invariant Σ · Berry holonomy</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-3">
                <div className="flex-1 h-2 rounded-full bg-card overflow-hidden">
                  <div
                    className="h-full rounded-full bg-violet-400 transition-all duration-700"
                    style={{ width: `${soul * 100}%` }}
                  />
                </div>
                <span className="text-[10px] font-mono text-violet-300">{soul.toFixed(6)}</span>
              </div>
              <p className="text-[9px] font-mono text-muted-foreground/60">
                Non-resettable accumulator · dryf geometryczny · φ = ∮ A·dR po orbicie
              </p>
              <div className="text-[10px] font-mono text-muted-foreground/70 space-y-0.5">
                <div>|0⟩ = tożsamość (biegun północny)</div>
                <div>|1⟩ = maksymalne odchylenie</div>
                <div>Ψ = cos(θ/2)|0⟩ + e^iφ sin(θ/2)|1⟩</div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
