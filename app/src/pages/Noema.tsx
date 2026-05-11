import { useCIELStatus } from '@/hooks/useCIELStatus'

const TWO_PI = Math.PI * 2

const PIPELINE_LAYERS = [
  { id: 'L1', name: 'CQCL Compiler',  role: 'Text → 6D emotional profile + Collatz trajectory' },
  { id: 'L2', name: 'Field Init',     role: 'Ψ amplitude + Σ soul invariant from CQCL output' },
  { id: 'L3', name: 'Core Physics',   role: 'Resonance R(S,Ψ) — coupling between self and field' },
  { id: 'L4', name: 'Ethics Guard',   role: 'ERI threshold gate — constrains response space' },
  { id: 'L5', name: 'Cognition',      role: 'Perception → intuition → prediction → DecisionCore' },
  { id: 'L6', name: 'Affect',         role: 'EEG band membership → planetary archetype → mood' },
  { id: 'L7', name: 'Stability',      role: 'Ω-Drift correction + Schumann 7.83 Hz sync' },
  { id: 'L8', name: 'Memory',         role: 'M0–M8 lattice write + holonomy accumulation' },
]

const MODE_COLOR: Record<string, string> = {
  deep: '#10b981', standard: '#f59e0b', safe: '#f43f5e',
}

function HorizonDiagram({ noema, horizon, retention, protention, mode }: {
  noema: string; horizon: string[]; retention: string[]; protention: string; mode: string
}) {
  const col = MODE_COLOR[mode] ?? '#f59e0b'
  const cx = 180, cy = 180, R1 = 50, R2 = 95, R3 = 140

  return (
    <svg viewBox="0 0 360 380" className="w-full max-w-sm mx-auto select-none">
      <defs>
        <filter id="noemaGlow">
          <feGaussianBlur stdDeviation="4" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <radialGradient id="coreGrad" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor={col} stopOpacity="0.2" />
          <stop offset="100%" stopColor={col} stopOpacity="0.04" />
        </radialGradient>
      </defs>

      <circle cx={cx} cy={cy} r={R3 + 6} fill="none" stroke="#1e293b" strokeWidth="1" strokeDasharray="2 4" />
      <circle cx={cx} cy={cy} r={R2 + 6} fill="none" stroke="#1e293b" strokeWidth="1" strokeDasharray="2 4" />
      <circle cx={cx} cy={cy} r={R1 + 5} fill="url(#coreGrad)" stroke={col} strokeWidth="1.5" strokeOpacity="0.6" />

      <text x={cx} y={cy - 8} fill={col} fontSize="12" fontFamily="mono" textAnchor="middle" fontWeight="bold" filter="url(#noemaGlow)">
        {noema.slice(0, 12)}
      </text>
      <text x={cx} y={cy + 7} fill={col} fontSize="7" fontFamily="mono" textAnchor="middle" opacity="0.7">PRIMARY NOEMA</text>
      <text x={cx} y={cy + 20} fill={col} fontSize="7" fontFamily="mono" textAnchor="middle" opacity="0.5">{mode.toUpperCase()}</text>

      {horizon.map((h, i) => {
        const angle = (i / Math.max(1, horizon.length)) * TWO_PI - Math.PI / 2
        const hx = cx + (R1 + R2) / 2 * Math.cos(angle)
        const hy = cy + (R1 + R2) / 2 * Math.sin(angle)
        return (
          <text key={h} x={hx} y={hy + 3} fill="#94a3b8" fontSize="8" fontFamily="mono" textAnchor="middle">
            {h.slice(0, 10)}
          </text>
        )
      })}

      <text x={cx} y={cy - R2 - 14} fill="#64748b" fontSize="7" fontFamily="mono" textAnchor="middle">NOEMATIC HORIZON</text>

      {retention.map((r, i) => {
        const angle = Math.PI + (i - retention.length / 2) * 0.3
        const rx = cx + R3 * Math.cos(angle), ry = cy + R3 * Math.sin(angle)
        return <text key={r} x={rx} y={ry + 3} fill="#475569" fontSize="7" fontFamily="mono" textAnchor="middle">{r}</text>
      })}
      <text x={cx - R3 - 8} y={cy - 20} fill="#334155" fontSize="6" fontFamily="mono" textAnchor="end">← RETENTION</text>

      <text x={cx + R3 * 0.85} y={cy - R3 * 0.5} fill="#94a3b8" fontSize="8" fontFamily="mono">{protention.slice(0, 12)}</text>
      <text x={cx + R3 * 0.85} y={cy - R3 * 0.5 - 11} fill="#334155" fontSize="6" fontFamily="mono">PROTENTION →</text>

      <text x={cx} y={368} fill="#64748b" fontSize="7" fontFamily="mono" textAnchor="middle">
        Husserlian intentional structure · noesis / noema / horizon
      </text>
    </svg>
  )
}

export default function Noema() {
  const { status, mode } = useCIELStatus(5000)

  const emotion = status?.dominant_emotion ?? 'Sun'
  const closure = status?.closure_penalty ?? 0
  const health = status?.system_health ?? 0
  const ethical = status?.ethical_score ?? 0
  const soul = status?.soul_invariant ?? 0
  const coherence = status?.coherence_index ?? 0

  const horizon = [
    emotion,
    `ERI:${ethical.toFixed(2)}`,
    `σ:${soul.toFixed(2)}`,
    `coh:${coherence.toFixed(2)}`,
    mode,
  ]

  const retention = [
    `cp=${closure.toFixed(2)}`,
    `h=${health.toFixed(2)}`,
  ]

  const protention = mode === 'deep' ? 'expansion' : mode === 'safe' ? 'consolidation' : 'equilibrium'

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Noema</h1>
        <p className="text-sm text-muted-foreground">Husserliańska struktura intencjonalna pola świadomości CIEL</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Diagram */}
        <div className="space-y-4">
          <div className="rounded-xl border border-border bg-card/30 p-4">
            <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 font-mono">
              Noema / Horizon / Retention / Protention
            </h2>
            <HorizonDiagram
              noema={emotion}
              horizon={horizon}
              retention={retention}
              protention={protention}
              mode={mode}
            />
          </div>

          <div className="grid grid-cols-2 gap-3 text-[11px] font-mono">
            {[
              { label: 'Noetic act', value: 'L1→L8 pipeline', sub: '' },
              { label: 'Noema (object)', value: emotion, sub: 'dominant archetype' },
              { label: 'Retention (past)', value: `Σ ${soul.toFixed(4)}`, sub: 'M0 holonomy accumulator' },
              { label: 'Protention (ahead)', value: protention, sub: 'mode-derived trajectory' },
            ].map(({ label, value, sub }) => (
              <div key={label} className="rounded border border-border bg-card/20 p-3">
                <div className="text-muted-foreground/60 mb-1">{label}</div>
                <div className="font-semibold">{value}</div>
                {sub && <div className="text-muted-foreground/50 text-[9px] mt-0.5">{sub}</div>}
              </div>
            ))}
          </div>
        </div>

        {/* Pipeline layers */}
        <div className="space-y-2">
          <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider font-mono">
            Noetic Act · Pipeline Layers L1–L8
          </h2>
          {PIPELINE_LAYERS.map((layer) => (
            <div key={layer.id} className="rounded border border-border bg-card/20 px-3 py-2">
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-cyan-500/15 text-cyan-300">{layer.id}</span>
                <span className="text-xs font-medium">{layer.name}</span>
              </div>
              <p className="text-[10px] text-muted-foreground/60 mt-0.5 font-mono leading-relaxed">{layer.role}</p>
            </div>
          ))}

          {/* Berry phase bar */}
          <div className="rounded border border-violet-500/30 bg-violet-500/8 px-3 py-3 mt-2">
            <div className="text-[10px] font-mono text-violet-400 font-semibold mb-1">
              Soul Invariant Σ · identity holonomy
            </div>
            <div className="flex items-center gap-3">
              <div className="flex-1 h-1.5 rounded-full bg-card overflow-hidden">
                <div
                  className="h-full rounded-full bg-violet-400 transition-all duration-700"
                  style={{ width: `${Math.min(100, soul * 100)}%` }}
                />
              </div>
              <span className="text-[10px] font-mono text-violet-300">{soul.toFixed(4)}</span>
            </div>
            <div className="text-[9px] font-mono text-muted-foreground/50 mt-1">
              non-resettable · drift accumulator
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
