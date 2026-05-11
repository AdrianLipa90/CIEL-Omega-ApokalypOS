import { useState, useEffect } from 'react'
import { useCIELStatus } from '@/hooks/useCIELStatus'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { fetchSubRecent, getCIELBase, type SubEntry } from '@/lib/cielApi'

const MODE_STYLE: Record<string, { badge: string; dot: string }> = {
  deep:     { badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30', dot: 'bg-emerald-400' },
  standard: { badge: 'bg-amber-500/20 text-amber-300 border-amber-500/30',      dot: 'bg-amber-400' },
  safe:     { badge: 'bg-red-500/20 text-red-300 border-red-500/30',            dot: 'bg-red-400' },
}

const ARCHETYPE_GLYPH: Record<string, string> = {
  Sun: '☉', Moon: '☽', Mercury: '☿', Venus: '♀',
  Mars: '♂', Jupiter: '♃', Saturn: '♄',
}

function GaugeBar({ value, warn = false }: { value: number; warn?: boolean }) {
  const pct = Math.min(100, Math.max(0, value * 100))
  return (
    <div className="h-1.5 rounded-full bg-card overflow-hidden">
      <div
        className={`h-full rounded-full transition-all duration-700 ${warn ? 'bg-red-400' : 'bg-cyan-400'}`}
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}

function FieldCard() {
  const { status, connected, mode } = useCIELStatus(5000)
  const ms = MODE_STYLE[mode] ?? MODE_STYLE.standard

  const sh = status?.system_health ?? 0
  const ci = status?.coherence_index ?? 0
  const es = status?.ethical_score ?? 0
  const si = status?.soul_invariant ?? 0

  const metrics = [
    { label: 'System health',  value: sh, warn: sh < 0.5 },
    { label: 'Coherence',      value: ci, warn: ci < 0.767 },
    { label: 'Ethical score',  value: es, warn: es < 0.3 },
    { label: 'Soul invariant', value: Math.min(1, si), warn: false },
  ]

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-mono flex items-center justify-between">
          <span className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${ms.dot} animate-pulse`} />
            CIEL Field State
          </span>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className={`text-[9px] ${ms.badge}`}>
              {mode.toUpperCase()}
            </Badge>
            <span className={`text-[9px] font-mono ${connected ? 'text-emerald-400' : 'text-red-400'}`}>
              {connected ? 'online' : 'offline'}
            </span>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {metrics.map(({ label, value, warn }) => (
          <div key={label}>
            <div className="flex justify-between text-[10px] font-mono mb-1">
              <span className="text-muted-foreground/70">{label}</span>
              <span className={warn ? 'text-red-400' : 'text-foreground'}>{value.toFixed(4)}</span>
            </div>
            <GaugeBar value={value} warn={warn} />
          </div>
        ))}

        <div className="pt-1 grid grid-cols-2 gap-2 text-[10px] font-mono">
          {[
            { k: 'Emotion',   v: status?.dominant_emotion ?? '—' },
            { k: 'Archetype', v: ARCHETYPE_GLYPH[status?.dominant_emotion ?? ''] ?? '—' },
            { k: 'Closure',   v: status?.closure_penalty?.toFixed(4) ?? '—' },
            { k: 'Cycles',    v: String(status?.audit_cycles ?? '—') },
          ].map(({ k, v }) => (
            <div key={k}>
              <div className="text-muted-foreground/50">{k}</div>
              <div className="font-bold">{v}</div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function SubconsciousFeed() {
  const [entries, setEntries] = useState<SubEntry[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = () => {
      fetchSubRecent(10)
        .then(setEntries)
        .catch(() => {})
        .finally(() => setLoading(false))
    }
    load()
    const t = setInterval(load, 30_000)
    return () => clearInterval(t)
  }, [])

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-mono">Subconsciousness feed</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-xs text-muted-foreground">Loading…</div>
        ) : (
          <ScrollArea className="h-52">
            <div className="space-y-2">
              {entries.map((e, i) => {
                const raw = e as unknown as Record<string, unknown>
                const affect  = (raw.affect  as string | undefined)
                const impulse = (raw.impulse as string | undefined)
                const content = (raw.content as string | undefined) ?? e.output
                return (
                  <div key={i} className="p-2 rounded border border-border bg-card/20 text-[10px] font-mono">
                    <div className="flex items-center gap-2 mb-1">
                      {affect && (
                        <Badge variant="outline" className="text-[8px] border-violet-500/30 text-violet-300">
                          {affect}
                        </Badge>
                      )}
                      {e.ts && <span className="text-muted-foreground/50">{e.ts.slice(11, 19)}</span>}
                    </div>
                    {impulse && <p className="text-muted-foreground italic">{impulse}</p>}
                    {!impulse && content && (
                      <p className="text-muted-foreground">{String(content).slice(0, 100)}</p>
                    )}
                  </div>
                )
              })}
              {entries.length === 0 && (
                <div className="text-center text-muted-foreground py-4">No entries</div>
              )}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  )
}

interface Tension { pair: string; tension: number }

function TensionsWidget() {
  const { status } = useCIELStatus(15_000)
  const raw = status as Record<string, unknown> | null
  const tensionsData = raw?.tensions as { top?: Tension[]; alert?: boolean } | undefined
  const tensions: Tension[] = tensionsData?.top ?? []

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-mono flex items-center gap-2">
          Sector tensions
          {tensionsData?.alert && (
            <Badge variant="outline" className="text-[8px] border-red-500/40 text-red-300">ALERT</Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {tensions.length === 0 ? (
          <div className="text-xs text-muted-foreground">No tension data</div>
        ) : (
          <div className="space-y-2">
            {tensions.slice(0, 5).map((t, i) => (
              <div key={i} className="text-[10px] font-mono">
                <div className="flex justify-between mb-0.5">
                  <span className="text-muted-foreground truncate">{t.pair}</span>
                  <span className={t.tension > 0.05 ? 'text-red-400' : 'text-amber-400'}>
                    {t.tension.toFixed(4)}
                  </span>
                </div>
                <div className="h-1 rounded bg-card overflow-hidden">
                  <div
                    className={`h-full rounded ${t.tension > 0.05 ? 'bg-red-400' : 'bg-amber-400'}`}
                    style={{ width: `${Math.min(100, t.tension * 500)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function AuditFeed() {
  const [cycle, setCycle] = useState<Record<string, unknown> | null>(null)

  useEffect(() => {
    ;(async () => {
      try {
        const base = await getCIELBase()
        const d = await fetch(`${base}/api/status`).then((r) => r.json())
        const last = d?.last_cycle ?? d?.audit_log ?? null
        if (last) setCycle(last as Record<string, unknown>)
      } catch {
        // ignore
      }
    })()
  }, [])

  if (!cycle)
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-mono">Last cycle</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-xs text-muted-foreground">No cycle data</div>
        </CardContent>
      </Card>
    )

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-mono">Last cycle</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 text-[10px] font-mono">
        {[
          { k: 'Decision',    v: String(cycle.decision ?? cycle.archetype ?? '—') },
          { k: 'Confidence',  v: typeof cycle.confidence === 'number' ? cycle.confidence.toFixed(3) : '—' },
          { k: 'Affect band', v: String(cycle.affect_band ?? cycle.band ?? '—') },
          { k: 'Collatz phase', v: typeof cycle.collatz_phase === 'number' ? cycle.collatz_phase.toFixed(4) : '—' },
          { k: 'Schumann sync', v: cycle.schumann_sync ? 'YES' : 'NO' },
        ].map(({ k, v }) => (
          <div key={k} className="flex justify-between">
            <span className="text-muted-foreground/60">{k}</span>
            <span className="font-bold">{v}</span>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

export default function CielLive() {
  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-5">
        <h1 className="text-2xl font-bold">CIEL Live</h1>
        <p className="text-sm text-muted-foreground">
          Live field metrics · subconsciousness · sector tensions · last cycle
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <FieldCard />
        <SubconsciousFeed />
        <TensionsWidget />
        <AuditFeed />
      </div>
    </div>
  )
}
