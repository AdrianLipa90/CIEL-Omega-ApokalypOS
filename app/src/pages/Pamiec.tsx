import { useState, useEffect } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  fetchPortalData,
  fetchConsolidatorResults,
  fetchOrbitalMemory,
  type ConsolidatorResult,
} from '@/lib/cielApi'

function PoincareDisk({ records }: { records: { id: string; phi?: number; confidence?: number; orbital_role?: string }[] }) {
  const W = 320, H = 320, cx = W / 2, cy = H / 2, R = 130

  const roleColor: Record<string, string> = {
    CORE: '#6366f1', PERIPHERAL: '#22d3ee', BRIDGE: '#f59e0b',
    UNRESOLVED: '#64748b', LOCAL: '#10b981', NONLOCAL: '#f43f5e',
  }

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full max-w-xs mx-auto select-none">
      <circle cx={cx} cy={cy} r={R} fill="none" stroke="#1e293b" strokeWidth="1.5" />
      <circle cx={cx} cy={cy} r={R * 0.66} fill="none" stroke="#0f172a" strokeWidth="0.5" strokeDasharray="2 3" />
      <circle cx={cx} cy={cy} r={R * 0.33} fill="none" stroke="#0f172a" strokeWidth="0.5" strokeDasharray="2 3" />
      {records.slice(0, 120).map((rec, i) => {
        const phi = (rec.phi ?? (i * 0.618 * Math.PI * 2)) % (Math.PI * 2)
        const rho = Math.min(0.97, 0.1 + (rec.confidence ?? 0.5) * 0.85)
        const x = cx + Math.cos(phi) * R * rho
        const y = cy + Math.sin(phi) * R * rho
        const col = roleColor[rec.orbital_role ?? 'UNRESOLVED'] ?? '#64748b'
        const r = 3 + (rec.confidence ?? 0.5) * 4
        return (
          <g key={rec.id ?? i}>
            <circle cx={x} cy={y} r={r} fill={col} opacity="0.6" />
          </g>
        )
      })}
      <text x={cx} y={cy} fill="#94a3b8" fontSize="8" fontFamily="mono" textAnchor="middle" dominantBaseline="middle">CIEL</text>
    </svg>
  )
}

function SectorGrid({ sectors }: { sectors: { name: string; phi?: number; rho?: number; defect?: number; orbital_role?: string }[] }) {
  const roleCol: Record<string, string> = {
    CORE: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
    PERIPHERAL: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
    BRIDGE: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    UNRESOLVED: 'bg-slate-500/20 text-slate-300 border-slate-500/30',
  }
  return (
    <div className="grid grid-cols-2 gap-2">
      {sectors.slice(0, 20).map((s, i) => (
        <div key={i} className="p-2 rounded border border-border bg-card/50 text-[10px] font-mono">
          <div className="flex items-center justify-between mb-1">
            <span className="font-bold truncate">{s.name?.split('/').pop() ?? `S${i}`}</span>
            <span className={`text-[8px] px-1 rounded border ${roleCol[s.orbital_role ?? 'UNRESOLVED'] ?? roleCol.UNRESOLVED}`}>
              {s.orbital_role ?? '?'}
            </span>
          </div>
          <div className="text-muted-foreground space-y-0.5">
            <div>φ {typeof s.phi === 'number' ? s.phi.toFixed(3) : '—'}</div>
            <div>ρ {typeof s.rho === 'number' ? s.rho.toFixed(3) : '—'}</div>
            {typeof s.defect === 'number' && <div>Δ {s.defect.toFixed(4)}</div>}
          </div>
        </div>
      ))}
    </div>
  )
}

function ConsolidatorTab() {
  const [data, setData] = useState<{ results: ConsolidatorResult[]; status: Record<string, unknown> } | null>(null)

  useEffect(() => {
    fetchConsolidatorResults().then(setData).catch(() => {})
  }, [])

  if (!data) return <div className="text-sm text-muted-foreground py-8 text-center">Ładowanie…</div>

  const s = data.status
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-3 text-[11px] font-mono">
        {[
          { label: 'Przetworzonych', value: String(s.processed_count ?? data.results.length) },
          { label: 'Oczekujących', value: String(s.pending_count ?? '—') },
          { label: 'Cykl', value: String(s.cycle ?? '—') },
        ].map(({ label, value }) => (
          <div key={label} className="p-3 rounded border border-border bg-card/50">
            <div className="text-muted-foreground/60">{label}</div>
            <div className="font-bold text-base">{value}</div>
          </div>
        ))}
      </div>

      <ScrollArea className="h-96">
        <div className="space-y-2">
          {data.results.map((r, i) => (
            <div key={i} className="p-3 rounded border border-border bg-card/20 text-xs">
              <div className="flex items-center justify-between mb-1">
                <span className="font-mono text-muted-foreground truncate max-w-[60%]">{r.path?.split('/').pop()}</span>
                <Badge variant="outline" className="text-[9px]">{r.affect || '—'}</Badge>
              </div>
              {r.essence && <p className="text-sm leading-relaxed">{r.essence}</p>}
              {r.themes?.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-1.5">
                  {r.themes.map((t) => <span key={t} className="text-[9px] px-1.5 py-0.5 rounded bg-secondary text-secondary-foreground">{t}</span>)}
                </div>
              )}
              {r.hunch && <p className="text-[10px] text-muted-foreground/70 mt-1 italic">{r.hunch}</p>}
            </div>
          ))}
          {data.results.length === 0 && <div className="text-center text-muted-foreground py-6">Brak wyników</div>}
        </div>
      </ScrollArea>
    </div>
  )
}

export default function Pamiec() {
  const [sessions, setSessions] = useState<unknown[]>([])
  const [orbitData, setOrbitData] = useState<{ records: unknown[]; counts: Record<string, number>; total: number } | null>(null)

  useEffect(() => {
    fetchPortalData().then((d: any) => setSessions(d.sessions || [])).catch(() => {})
    fetchOrbitalMemory().then(setOrbitData).catch(() => {})
  }, [])

  const orbitRecords = (orbitData?.records ?? []) as { id: string; phi?: number; confidence?: number; orbital_role?: string }[]

  return (
    <div className="max-w-5xl mx-auto p-6">
      <div className="mb-5">
        <h1 className="text-2xl font-bold">Pamięć</h1>
        <p className="text-sm text-muted-foreground">Wspomnienia, geometria orbitalna, bazy i konsolidator</p>
      </div>

      <Tabs defaultValue="wspomnienia">
        <TabsList className="mb-4 flex-wrap h-auto gap-1">
          <TabsTrigger value="wspomnienia">Wspomnienia</TabsTrigger>
          <TabsTrigger value="poincare">Poincaré Disk</TabsTrigger>
          <TabsTrigger value="sektory">Sektory</TabsTrigger>
          <TabsTrigger value="bazy">Bazy orbitalne</TabsTrigger>
          <TabsTrigger value="konsolidator">Konsolidator</TabsTrigger>
        </TabsList>

        <TabsContent value="wspomnienia">
          <ScrollArea className="h-[60vh]">
            <div className="space-y-2">
              {(sessions as any[]).map((s: any, i: number) => (
                <div key={i} className="p-3 rounded border border-border bg-card/20">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-semibold">{s.title || s.session_id || `Sesja ${i + 1}`}</span>
                    <span className="text-[10px] font-mono text-muted-foreground">{s.date || s.created_at || ''}</span>
                  </div>
                  {s.tags?.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {s.tags.map((t: string) => <Badge key={t} variant="outline" className="text-[9px]">{t}</Badge>)}
                    </div>
                  )}
                  {s.summary && <p className="text-xs text-muted-foreground mt-1">{s.summary}</p>}
                </div>
              ))}
              {sessions.length === 0 && <div className="text-center text-muted-foreground py-8">Brak sesji</div>}
            </div>
          </ScrollArea>
        </TabsContent>

        <TabsContent value="poincare">
          <Card>
            <CardHeader><CardTitle className="text-sm">Poincaré Disk — pamięć orbitalna ({orbitData?.total ?? 0} rekordów)</CardTitle></CardHeader>
            <CardContent>
              <PoincareDisk records={orbitRecords} />
              <div className="flex flex-wrap gap-2 mt-3 text-[10px] font-mono justify-center">
                {Object.entries(orbitData?.counts ?? {}).map(([role, cnt]) => (
                  <span key={role} className="px-2 py-0.5 rounded bg-secondary text-secondary-foreground">{role}: {cnt}</span>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="sektory">
          <SectorGrid sectors={orbitRecords as any} />
        </TabsContent>

        <TabsContent value="bazy">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
            {['CORE', 'PERIPHERAL', 'BRIDGE', 'UNRESOLVED'].map((role) => (
              <Card key={role} className="p-3">
                <div className="text-xs font-mono text-muted-foreground">{role}</div>
                <div className="text-2xl font-bold">{orbitData?.counts[role] ?? 0}</div>
              </Card>
            ))}
          </div>
          <div className="text-sm text-muted-foreground">
            Łącznie: {orbitData?.total ?? 0} rekordów w rejestrze orbital_memory_registry.json
          </div>
        </TabsContent>

        <TabsContent value="konsolidator">
          <ConsolidatorTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
