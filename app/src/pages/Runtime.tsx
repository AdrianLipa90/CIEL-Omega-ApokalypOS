import { useState } from 'react'
import { useCIELStatus } from '@/hooks/useCIELStatus'
import { runPipeline } from '@/lib/cielApi'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Play, Loader2, ShieldCheck, Infinity as InfIcon, Cpu, Activity, Database, Compass } from 'lucide-react'

const MODE_STYLE: Record<string, { cls: string; label: string; dot: string }> = {
  deep:     { cls: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300', label: 'DEEP MODE',     dot: 'bg-emerald-400' },
  standard: { cls: 'border-amber-500/40  bg-amber-500/10  text-amber-300',  label: 'STANDARD MODE', dot: 'bg-amber-400'  },
  safe:     { cls: 'border-rose-500/40   bg-rose-500/10   text-rose-300',   label: 'SAFE MODE',     dot: 'bg-rose-400'   },
}

const M_LAYERS = [
  { id: 'M0', name: 'Quantum Identity',  desc: 'Berry phase ∈ [0,4π) — non-resettable identity holonomy' },
  { id: 'M1', name: 'Affective',         desc: '8-class dominant emotion + E_monitor' },
  { id: 'M2', name: 'Episodic',          desc: 'Geometric trace of cycle (no content)' },
  { id: 'M3', name: 'Semantic',          desc: 'Hebbian concept-cluster updates' },
  { id: 'M4', name: 'Procedural',        desc: 'Pipeline procedure templates' },
  { id: 'M5', name: 'System Health',     desc: 'Composite health × closure penalty' },
  { id: 'M6', name: 'Affective Key',     desc: 'Pre-pipeline prompt fingerprint (subconscious daemon)' },
  { id: 'M7', name: 'Semantic Key',      desc: 'Post-pipeline topic tags (BRAID)' },
  { id: 'M8', name: 'Audit Trail',       desc: 'Append-only journal (Iron Law of Memory Integrity)' },
]

function GaugeBar({ value, max = 1, col }: { value: number; max?: number; col: string }) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100))
  return (
    <div className="h-1.5 rounded-full bg-card overflow-hidden">
      <div className={`h-full rounded-full transition-all duration-700 ${col}`} style={{ width: `${pct}%` }} />
    </div>
  )
}

function MetricCard({ icon: Icon, label, value, suffix, tag, tagOk }: {
  icon: typeof Activity; label: string; value: string; suffix?: string; tag?: string; tagOk?: boolean
}) {
  return (
    <div className="p-4 rounded-xl border border-border bg-card flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <Icon className="w-4 h-4 text-cyan-400" />
        {tag && (
          <span className={`text-[10px] font-mono font-bold ${tagOk ? 'text-emerald-400' : 'text-rose-400'}`}>{tag}</span>
        )}
      </div>
      <div className="text-xl font-bold font-mono">
        {value}{suffix && <span className="text-sm text-muted-foreground ml-1">{suffix}</span>}
      </div>
      <div className="text-[10px] text-muted-foreground uppercase tracking-wide">{label}</div>
    </div>
  )
}

export default function Runtime() {
  const { status, mode, refresh } = useCIELStatus(4000)
  const [busy, setBusy] = useState(false)
  const [runLog, setRunLog] = useState('')

  const ms = MODE_STYLE[mode]
  const closure = status?.closure_penalty ?? 0
  const health = status?.system_health ?? 0
  const coherence = status?.coherence_index ?? 0
  const ethical = status?.ethical_score ?? 0
  const soul = status?.soul_invariant ?? 0

  async function firePipeline() {
    setBusy(true)
    setRunLog('')
    try {
      const r = await runPipeline('ciel_pipeline')
      setRunLog((r as Record<string,unknown>).out as string || r.stdout || 'OK')
      await refresh()
    } catch (e) {
      setRunLog(String(e))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Runtime Dashboard</h1>
          <p className="text-sm text-muted-foreground">Live telemetry z silnika CIEL/Ω</p>
        </div>
        <div className={`flex items-center gap-2 px-3 py-1.5 border rounded text-sm font-mono font-bold ${ms.cls}`}>
          <div className={`w-2 h-2 rounded-full animate-pulse ${ms.dot}`} />
          {ms.label}
        </div>
      </div>

      {/* Pipeline trigger */}
      <Card>
        <CardContent className="pt-4 space-y-3">
          <div className="flex items-center justify-between text-sm font-semibold text-muted-foreground uppercase tracking-wide">
            <span>Uruchom Pipeline</span>
          </div>
          <div className="flex gap-2">
            <Button onClick={firePipeline} disabled={busy} className="flex items-center gap-2">
              {busy ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              {busy ? 'Działa…' : 'Uruchom ciel_pipeline'}
            </Button>
          </div>
          {runLog && (
            <pre className="text-[10px] font-mono bg-card border border-border rounded p-2 max-h-32 overflow-auto text-muted-foreground whitespace-pre-wrap">
              {runLog}
            </pre>
          )}
        </CardContent>
      </Card>

      {/* 6 metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <MetricCard icon={InfIcon}    label="Identity Phase (M0)" value={closure.toFixed(3)} suffix="cp" tag={mode.toUpperCase()} tagOk={mode === 'deep'} />
        <MetricCard icon={Activity}   label="System Health"        value={health.toFixed(3)}    tag={health >= 0.5 ? 'OK' : 'LOW'}   tagOk={health >= 0.5} />
        <MetricCard icon={ShieldCheck} label="Ethical Score (ERI)" value={ethical.toFixed(3)}   tag={ethical >= 0.4 ? 'PASS' : 'BLOCK'} tagOk={ethical >= 0.4} />
        <MetricCard icon={Cpu}         label="Coherence Index"     value={coherence.toFixed(3)} tag={coherence >= 0.767 ? 'healthy' : 'low'} tagOk={coherence >= 0.767} />
        <MetricCard icon={Compass}     label="Soul Invariant (Σ)"  value={soul.toFixed(3)} />
        <MetricCard icon={Database}    label="Backend"             value={status?.backend_status ?? '—'} />
      </div>

      {/* Metrics gauges */}
      <Card>
        <CardHeader><CardTitle className="text-sm">Metryki systemowe</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          {[
            { label: 'System Health', value: health, col: health >= 0.5 ? 'bg-emerald-400' : 'bg-rose-400' },
            { label: 'Coherence Index', value: coherence, col: coherence >= 0.767 ? 'bg-cyan-400' : 'bg-amber-400' },
            { label: 'Ethical Score', value: ethical, col: ethical >= 0.4 ? 'bg-violet-400' : 'bg-rose-400' },
            { label: 'Soul Invariant', value: soul, col: 'bg-indigo-400' },
          ].map(({ label, value, col }) => (
            <div key={label} className="space-y-1">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-muted-foreground">{label}</span>
                <span>{value.toFixed(4)}</span>
              </div>
              <GaugeBar value={value} col={col} />
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Memory Lattice M0–M8 */}
      <Card>
        <CardHeader><CardTitle className="text-sm flex items-center gap-2"><Database className="w-4 h-4 text-violet-400" />Memory Lattice M0–M8</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {M_LAYERS.map((m) => (
            <div key={m.id} className="flex items-start gap-3 p-2 rounded border border-border bg-background">
              <span className="text-xs font-mono font-bold text-violet-400 w-7 shrink-0 mt-0.5">{m.id}</span>
              <div>
                <div className="text-sm font-semibold">{m.name}</div>
                <div className="text-xs text-muted-foreground">{m.desc}</div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* System info */}
      <Card>
        <CardHeader><CardTitle className="text-sm">System Info</CardTitle></CardHeader>
        <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
          {[
            { label: 'Mode', value: status?.system_mode ?? '—' },
            { label: 'Backend', value: status?.backend_status ?? '—' },
            { label: 'Closure', value: closure.toFixed(4) },
            { label: 'Energy', value: status?.energy_budget ?? '—' },
            { label: 'Emotion', value: status?.dominant_emotion ?? '—' },
            { label: 'Manifest', value: status?.manifest_version ?? '—' },
            { label: 'Sub affect', value: (status as any)?.sub_affect || '—' },
            { label: 'HTRI coh', value: (status as any)?.htri_coherence?.toFixed(3) || '—' },
          ].map(({ label, value }) => (
            <div key={label} className="p-2 rounded border border-border bg-card/50">
              <div className="text-muted-foreground/60 mb-0.5">{label}</div>
              <div className="font-bold truncate">{value}</div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
