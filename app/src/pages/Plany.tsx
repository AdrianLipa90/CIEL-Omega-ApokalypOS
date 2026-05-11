import { useState, useEffect } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import {
  fetchIntentions,
  addIntention,
  markIntentionDone,
  fetchProjects,
  addProject,
  fetchPortalData,
  fetchHunches,
  addHunch,
  type IntentionEntry,
  type ProjectEntry,
  type HunchEntry,
} from '@/lib/cielApi'

const PRIORITY_STYLE: Record<string, string> = {
  H: 'bg-red-500/20 text-red-300 border-red-500/30',
  M: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  L: 'bg-slate-500/20 text-slate-300 border-slate-500/30',
}

const STATUS_STYLE: Record<string, string> = {
  active: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  planned: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
  done: 'bg-slate-500/20 text-slate-300 border-slate-500/30',
  paused: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
}

// ── Intencje ─────────────────────────────────────────────────────────────────
function IntencjeTab() {
  const [items, setItems] = useState<IntentionEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [addOpen, setAddOpen] = useState(false)
  const [newText, setNewText] = useState('')
  const [newPriority, setNewPriority] = useState<'H' | 'M' | 'L'>('M')
  const [saving, setSaving] = useState(false)
  const [filter, setFilter] = useState<'all' | 'H' | 'M' | 'L'>('all')

  const load = () => {
    setLoading(true)
    fetchIntentions()
      .then(setItems)
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleDone = async (id: string) => {
    await markIntentionDone(id).catch(() => {})
    load()
  }

  const handleAdd = async () => {
    if (!newText.trim()) return
    setSaving(true)
    try {
      await addIntention(newText.trim(), newPriority)
      setNewText('')
      setAddOpen(false)
      load()
    } finally {
      setSaving(false)
    }
  }

  const filtered = filter === 'all' ? items : items.filter((i) => i.priority === filter)
  const pending = items.filter((i) => !i.done)
  const done = items.filter((i) => i.done)

  if (loading) return <div className="text-sm text-muted-foreground py-8 text-center">Ładowanie…</div>

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex gap-1 text-[10px] font-mono">
          {(['all', 'H', 'M', 'L'] as const).map((p) => (
            <button
              key={p}
              onClick={() => setFilter(p)}
              className={`px-2 py-1 rounded border transition-colors ${
                filter === p
                  ? 'border-cyan-500/40 bg-cyan-500/10 text-cyan-300'
                  : 'border-border text-muted-foreground'
              }`}
            >
              {p === 'all' ? `Wszystkie (${items.length})` : `${p} (${items.filter((i) => i.priority === p).length})`}
            </button>
          ))}
        </div>
        <Button size="sm" variant="outline" onClick={() => setAddOpen(true)}>+ Intencja</Button>
      </div>

      <div className="grid grid-cols-3 gap-2 text-[10px] font-mono mb-2">
        {[
          { label: 'Oczekujące', value: pending.length },
          { label: 'Wykonane', value: done.length },
          { label: 'Razem', value: items.length },
        ].map(({ label, value }) => (
          <div key={label} className="p-2 rounded border border-border bg-card/30">
            <div className="text-muted-foreground/60">{label}</div>
            <div className="font-bold text-base">{value}</div>
          </div>
        ))}
      </div>

      <ScrollArea className="h-[50vh]">
        <div className="space-y-2">
          {filtered.map((item, i) => (
            <div
              key={i}
              className={`p-3 rounded border text-xs flex items-start gap-3 ${
                item.done ? 'border-border/30 bg-card/10 opacity-50' : 'border-border bg-card/20'
              }`}
            >
              <input
                type="checkbox"
                checked={!!item.done}
                onChange={() => !item.done && item.id && handleDone(item.id)}
                className="mt-0.5 cursor-pointer"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Badge variant="outline" className={`text-[9px] ${PRIORITY_STYLE[item.priority]}`}>
                    {item.priority}
                  </Badge>
                  <span className={item.done ? 'line-through text-muted-foreground' : ''}>{item.text}</span>
                </div>
                {item.ts && (
                  <div className="text-[9px] text-muted-foreground/50 font-mono">{item.ts}</div>
                )}
              </div>
            </div>
          ))}
          {filtered.length === 0 && (
            <div className="text-center text-muted-foreground py-8">Brak intencji</div>
          )}
        </div>
      </ScrollArea>

      <Dialog open={addOpen} onOpenChange={setAddOpen}>
        <DialogContent className="sm:max-w-md border-border bg-card">
          <DialogHeader><DialogTitle className="text-sm font-mono">Nowa intencja</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <textarea
              className="w-full bg-background border border-border rounded p-3 text-sm font-mono resize-none focus:outline-none focus:ring-1 focus:ring-cyan-500/50 h-24"
              placeholder="Treść intencji…"
              value={newText}
              onChange={(e) => setNewText(e.target.value)}
            />
            <div className="flex gap-2">
              {(['H', 'M', 'L'] as const).map((p) => (
                <button
                  key={p}
                  onClick={() => setNewPriority(p)}
                  className={`flex-1 py-1.5 text-xs rounded border font-mono transition-colors ${
                    newPriority === p ? PRIORITY_STYLE[p] : 'border-border text-muted-foreground'
                  }`}
                >
                  {p === 'H' ? 'Wysoki' : p === 'M' ? 'Średni' : 'Niski'}
                </button>
              ))}
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="ghost" size="sm" onClick={() => setAddOpen(false)}>Anuluj</Button>
              <Button size="sm" onClick={handleAdd} disabled={saving || !newText.trim()}>
                {saving ? 'Dodaję…' : 'Dodaj'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

// ── Plany długo/krótkofalowe ─────────────────────────────────────────────────
function PlanyLongTab() {
  const [plans, setPlans] = useState<{ long: string[]; short: string[] } | null>(null)

  useEffect(() => {
    fetchPortalData()
      .then((d: any) => {
        setPlans({
          long: d.plans?.long ?? d.long_term_plans ?? [],
          short: d.plans?.short ?? d.short_term_plans ?? [],
        })
      })
      .catch(() => setPlans({ long: [], short: [] }))
  }, [])

  if (!plans) return <div className="text-sm text-muted-foreground py-8 text-center">Ładowanie…</div>

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {[
        { title: 'Długofalowe', items: plans.long, color: 'text-violet-400' },
        { title: 'Krótkofalowe', items: plans.short, color: 'text-cyan-400' },
      ].map(({ title, items, color }) => (
        <Card key={title}>
          <CardHeader><CardTitle className={`text-sm font-mono ${color}`}>{title}</CardTitle></CardHeader>
          <CardContent>
            <ScrollArea className="h-64">
              <ul className="space-y-2">
                {items.map((item, i) => (
                  <li key={i} className="text-xs font-mono text-muted-foreground flex items-start gap-2">
                    <span className={`${color} shrink-0 mt-0.5`}>›</span>
                    <span>{item}</span>
                  </li>
                ))}
                {items.length === 0 && (
                  <li className="text-center text-muted-foreground py-4">Brak planów</li>
                )}
              </ul>
            </ScrollArea>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

// ── Projekty ─────────────────────────────────────────────────────────────────
function ProjektyTab() {
  const [projects, setProjects] = useState<ProjectEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>('all')
  const [addOpen, setAddOpen] = useState(false)
  const [form, setForm] = useState({ name: '', desc: '', status: 'planned' as ProjectEntry['status'], tags: '' })
  const [saving, setSaving] = useState(false)

  const load = () => {
    setLoading(true)
    fetchProjects().then(setProjects).catch(() => {}).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleAdd = async () => {
    if (!form.name.trim()) return
    setSaving(true)
    try {
      await addProject({
        name: form.name.trim(),
        desc: form.desc.trim(),
        status: form.status,
        tags: form.tags.split(',').map((t) => t.trim()).filter(Boolean),
      })
      setAddOpen(false)
      setForm({ name: '', desc: '', status: 'planned', tags: '' })
      load()
    } finally {
      setSaving(false)
    }
  }

  const statuses = ['all', 'active', 'planned', 'done', 'paused']
  const filtered = filter === 'all' ? projects : projects.filter((p) => p.status === filter)

  if (loading) return <div className="text-sm text-muted-foreground py-8 text-center">Ładowanie…</div>

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex flex-wrap gap-1 text-[10px] font-mono">
          {statuses.map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`px-2 py-1 rounded border transition-colors ${
                filter === s ? 'border-cyan-500/40 bg-cyan-500/10 text-cyan-300' : 'border-border text-muted-foreground'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
        <Button size="sm" variant="outline" onClick={() => setAddOpen(true)}>+ Projekt</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {filtered.map((p, i) => (
          <Card key={i} className="bg-card/20">
            <CardContent className="p-4">
              <div className="flex items-start justify-between gap-2 mb-2">
                <h3 className="font-semibold text-sm">{p.name}</h3>
                <Badge variant="outline" className={`text-[9px] shrink-0 ${STATUS_STYLE[p.status]}`}>
                  {p.status}
                </Badge>
              </div>
              {p.desc && <p className="text-xs text-muted-foreground mb-2">{p.desc}</p>}
              <div className="flex flex-wrap gap-1">
                {p.tags?.map((tag) => (
                  <span key={tag} className="text-[9px] px-1.5 py-0.5 rounded bg-secondary text-secondary-foreground">
                    {tag}
                  </span>
                ))}
              </div>
              {p.updated && (
                <div className="text-[9px] text-muted-foreground/50 font-mono mt-1">{p.updated}</div>
              )}
            </CardContent>
          </Card>
        ))}
        {filtered.length === 0 && (
          <div className="text-center text-muted-foreground py-8 col-span-2">Brak projektów</div>
        )}
      </div>

      <Dialog open={addOpen} onOpenChange={setAddOpen}>
        <DialogContent className="sm:max-w-md border-border bg-card">
          <DialogHeader><DialogTitle className="text-sm font-mono">Nowy projekt</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <input
              className="w-full bg-background border border-border rounded px-3 py-2 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-cyan-500/50"
              placeholder="Nazwa projektu"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
            <textarea
              className="w-full bg-background border border-border rounded p-3 text-sm font-mono resize-none focus:outline-none focus:ring-1 focus:ring-cyan-500/50 h-20"
              placeholder="Opis…"
              value={form.desc}
              onChange={(e) => setForm({ ...form, desc: e.target.value })}
            />
            <div className="flex gap-2 flex-wrap">
              {(['active', 'planned', 'done', 'paused'] as const).map((s) => (
                <button
                  key={s}
                  onClick={() => setForm({ ...form, status: s })}
                  className={`px-2 py-1 text-[10px] rounded border font-mono transition-colors ${
                    form.status === s ? STATUS_STYLE[s] : 'border-border text-muted-foreground'
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
            <input
              className="w-full bg-background border border-border rounded px-3 py-2 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-cyan-500/50"
              placeholder="Tagi (przecinkowe)"
              value={form.tags}
              onChange={(e) => setForm({ ...form, tags: e.target.value })}
            />
            <div className="flex justify-end gap-2">
              <Button variant="ghost" size="sm" onClick={() => setAddOpen(false)}>Anuluj</Button>
              <Button size="sm" onClick={handleAdd} disabled={saving || !form.name.trim()}>
                {saving ? 'Zapisuję…' : 'Zapisz'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

// ── Przeczucia ────────────────────────────────────────────────────────────────
function PrzeczuciaTab() {
  const [hunches, setHunches] = useState<HunchEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [text, setText] = useState('')
  const [saving, setSaving] = useState(false)

  const load = () => {
    setLoading(true)
    fetchHunches().then(setHunches).catch(() => {}).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleAdd = async () => {
    if (!text.trim()) return
    setSaving(true)
    try {
      await addHunch(text.trim(), [])
      setText('')
      load()
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="text-sm text-muted-foreground py-8 text-center">Ładowanie…</div>

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <input
          className="flex-1 bg-background border border-border rounded px-3 py-2 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-cyan-500/50"
          placeholder="Nowe przeczucie…"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleAdd()}
        />
        <Button size="sm" onClick={handleAdd} disabled={saving || !text.trim()}>
          {saving ? '…' : 'Dodaj'}
        </Button>
      </div>
      <ScrollArea className="h-[55vh]">
        <div className="space-y-2">
          {hunches.map((h, i) => (
            <div key={i} className="p-3 rounded border border-border bg-card/20 text-xs">
              <p className="font-mono leading-relaxed">{h.hunch}</p>
              {h.ts && (
                <div className="text-[9px] text-muted-foreground/50 font-mono mt-1">{h.ts}</div>
              )}
            </div>
          ))}
          {hunches.length === 0 && (
            <div className="text-center text-muted-foreground py-8">Brak przeczuć</div>
          )}
        </div>
      </ScrollArea>
    </div>
  )
}

// ── Main ──────────────────────────────────────────────────────────────────────
export default function Plany() {
  return (
    <div className="max-w-5xl mx-auto p-6">
      <div className="mb-5">
        <h1 className="text-2xl font-bold">Plany</h1>
        <p className="text-sm text-muted-foreground">Intencje, plany, projekty i przeczucia CIEL</p>
      </div>

      <Tabs defaultValue="intencje">
        <TabsList className="mb-4 flex-wrap h-auto gap-1">
          <TabsTrigger value="intencje">Aktywne intencje</TabsTrigger>
          <TabsTrigger value="plany">Plany</TabsTrigger>
          <TabsTrigger value="projekty">Projekty</TabsTrigger>
          <TabsTrigger value="przeczucia">Przeczucia</TabsTrigger>
        </TabsList>

        <TabsContent value="intencje"><IntencjeTab /></TabsContent>
        <TabsContent value="plany"><PlanyLongTab /></TabsContent>
        <TabsContent value="projekty"><ProjektyTab /></TabsContent>
        <TabsContent value="przeczucia"><PrzeczuciaTab /></TabsContent>
      </Tabs>
    </div>
  )
}
