import { useState, useEffect, useRef } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'
import {
  fetchConstraints,
  addConstraint,
  fetchRoutines,
  fetchDziennik,
  appendDziennik,
  type ConstraintEntry,
  type RoutinesData,
} from '@/lib/cielApi'

const TYPE_STYLE: Record<string, string> = {
  forbid: 'bg-red-500/20 text-red-300 border-red-500/30',
  obligate: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  wish: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
}

const TYPE_LABEL: Record<string, string> = {
  forbid: 'ZAKAZ',
  obligate: 'OBOWIĄZEK',
  wish: 'ŻYCZENIE',
}

function AddConstraintDialog({
  type,
  onAdded,
}: {
  type: 'forbid' | 'obligate' | 'wish'
  onAdded: () => void
}) {
  const [open, setOpen] = useState(false)
  const [text, setText] = useState('')
  const [tags, setTags] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    if (!text.trim()) return
    setSaving(true)
    try {
      await addConstraint({
        type,
        text: text.trim(),
        tags: tags
          .split(',')
          .map((t) => t.trim())
          .filter(Boolean),
        context: '',
      })
      setText('')
      setTags('')
      setOpen(false)
      onAdded()
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <Button size="sm" variant="outline" onClick={() => setOpen(true)}>
        + Dodaj
      </Button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-md border-border bg-card">
          <DialogHeader>
            <DialogTitle className="text-sm font-mono">
              Nowy {TYPE_LABEL[type].toLowerCase()}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-3">
            <textarea
              className="w-full bg-background border border-border rounded p-3 text-sm resize-none focus:outline-none focus:ring-1 focus:ring-cyan-500/50 h-28 font-mono"
              placeholder="Treść…"
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
            <input
              type="text"
              className="w-full bg-background border border-border rounded px-3 py-2 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-cyan-500/50"
              placeholder="Tagi (przecinkowe)"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
            />
            <div className="flex justify-end gap-2">
              <Button variant="ghost" size="sm" onClick={() => setOpen(false)}>
                Anuluj
              </Button>
              <Button size="sm" onClick={handleSave} disabled={saving || !text.trim()}>
                {saving ? 'Zapisuję…' : 'Zapisz'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}

function ConstraintList({ types }: { types: ('forbid' | 'obligate' | 'wish')[] }) {
  const [items, setItems] = useState<ConstraintEntry[]>([])
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    Promise.all(types.map((t) => fetchConstraints(t)))
      .then((results) => setItems(results.flat()))
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [])

  if (loading) return <div className="text-sm text-muted-foreground py-8 text-center">Ładowanie…</div>

  return (
    <div className="space-y-3">
      <div className="flex justify-end">
        <AddConstraintDialog type={types[0]} onAdded={load} />
      </div>
      <ScrollArea className="h-[55vh]">
        <div className="space-y-2">
          {items.map((item, i) => (
            <div key={i} className="p-3 rounded border border-border bg-card/20 text-xs">
              <div className="flex items-start justify-between gap-2 mb-1">
                <p className="font-mono text-sm leading-relaxed flex-1">{item.text}</p>
                <Badge
                  variant="outline"
                  className={`text-[9px] shrink-0 ${TYPE_STYLE[item.type] ?? ''}`}
                >
                  {TYPE_LABEL[item.type] ?? item.type}
                </Badge>
              </div>
              <div className="flex flex-wrap gap-1 mt-1.5">
                {item.tags?.map((tag) => (
                  <span
                    key={tag}
                    className="text-[9px] px-1.5 py-0.5 rounded bg-secondary text-secondary-foreground"
                  >
                    {tag}
                  </span>
                ))}
              </div>
              {item.ts && (
                <div className="text-[9px] text-muted-foreground/50 mt-1 font-mono">{item.ts}</div>
              )}
            </div>
          ))}
          {items.length === 0 && (
            <div className="text-center text-muted-foreground py-8">Brak wpisów</div>
          )}
        </div>
      </ScrollArea>
    </div>
  )
}

function RoutinesTab() {
  const [data, setData] = useState<RoutinesData | null>(null)

  useEffect(() => {
    fetchRoutines().then(setData).catch(() => {})
  }, [])

  if (!data) return <div className="text-sm text-muted-foreground py-8 text-center">Ładowanie…</div>

  return (
    <div className="space-y-3">
      {data.last_updated && (
        <div className="text-[10px] font-mono text-muted-foreground/60">
          Ostatnia aktualizacja: {data.last_updated}
        </div>
      )}
      <ScrollArea className="h-[58vh]">
        <Accordion type="multiple" className="space-y-2">
          {data.sections.map((section, i) => (
            <AccordionItem
              key={i}
              value={String(i)}
              className="border border-border rounded-lg px-1"
            >
              <AccordionTrigger className="px-3 text-sm font-semibold hover:no-underline">
                {section.name}
                <span className="ml-2 text-[10px] text-muted-foreground font-mono font-normal">
                  ({section.items.length})
                </span>
              </AccordionTrigger>
              <AccordionContent className="px-3 pb-3">
                <ul className="space-y-1.5">
                  {section.items.map((item, j) => (
                    <li key={j} className="text-xs text-muted-foreground font-mono leading-relaxed flex items-start gap-2">
                      <span className="text-cyan-500/60 mt-0.5 shrink-0">›</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </AccordionContent>
            </AccordionItem>
          ))}
          {data.sections.length === 0 && (
            <div className="text-center text-muted-foreground py-8">Brak rutyn</div>
          )}
        </Accordion>
      </ScrollArea>
    </div>
  )
}

function DziennikTab() {
  const [content, setContent] = useState('')
  const [draft, setDraft] = useState('')
  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(true)
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    fetchDziennik()
      .then((text: string) => {
        setContent(text)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  const handleAppend = async () => {
    if (!draft.trim()) return
    setSaving(true)
    try {
      await appendDziennik(draft.trim())
      const updated = await fetchDziennik()
      setContent(updated as string)
      setDraft('')
    } finally {
      setSaving(false)
    }
  }

  const handleDraftChange = (val: string) => {
    setDraft(val)
    if (saveTimer.current) clearTimeout(saveTimer.current)
  }

  if (loading) return <div className="text-sm text-muted-foreground py-8 text-center">Ładowanie…</div>

  return (
    <div className="space-y-4">
      <div className="rounded border border-border bg-card/20 p-1">
        <ScrollArea className="h-72">
          <pre className="text-xs font-mono text-muted-foreground leading-relaxed p-3 whitespace-pre-wrap">
            {content || '— dziennik pusty —'}
          </pre>
        </ScrollArea>
      </div>
      <div className="space-y-2">
        <textarea
          className="w-full bg-background border border-border rounded p-3 text-sm font-mono resize-none focus:outline-none focus:ring-1 focus:ring-cyan-500/50 h-28"
          placeholder="Nowy wpis między wierszami…"
          value={draft}
          onChange={(e) => handleDraftChange(e.target.value)}
        />
        <div className="flex justify-end">
          <Button
            size="sm"
            onClick={handleAppend}
            disabled={saving || !draft.trim()}
          >
            {saving ? 'Zapisuję…' : 'Dopisz'}
          </Button>
        </div>
      </div>
    </div>
  )
}

export default function Tozsamosc() {
  return (
    <div className="max-w-5xl mx-auto p-6">
      <div className="mb-5">
        <h1 className="text-2xl font-bold">Tożsamość</h1>
        <p className="text-sm text-muted-foreground">Zakazy, obowiązki, życzenia, rutyny i dziennik</p>
      </div>

      <Tabs defaultValue="zakazy">
        <TabsList className="mb-4 flex-wrap h-auto gap-1">
          <TabsTrigger value="zakazy">Zakazy i obowiązki</TabsTrigger>
          <TabsTrigger value="zyczenia">Życzenia CIEL</TabsTrigger>
          <TabsTrigger value="rutyny">Rutyny</TabsTrigger>
          <TabsTrigger value="dziennik">Między wierszami</TabsTrigger>
        </TabsList>

        <TabsContent value="zakazy">
          <ConstraintList types={['forbid', 'obligate']} />
        </TabsContent>

        <TabsContent value="zyczenia">
          <ConstraintList types={['wish']} />
        </TabsContent>

        <TabsContent value="rutyny">
          <RoutinesTab />
        </TabsContent>

        <TabsContent value="dziennik">
          <DziennikTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
