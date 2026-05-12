import { useState, useEffect } from 'react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Search, Link2 } from 'lucide-react'
import { getCIELBase } from '@/lib/cielApi'

interface ObjectCard {
  id: string
  name: string
  type: string
  path?: string
  description?: string
  dependencies?: string[]
  tags?: string[]
  orbital_role?: string
  info_mass?: number
  berry_phase?: number
  phi?: number
  rho?: number
  spin?: string
  // W_ij connections
  connections?: { target: string; w: number }[]
}

const TYPE_STYLE: Record<string, string> = {
  MODULE: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
  ENTITY: 'bg-violet-500/20 text-violet-300 border-violet-500/30',
  CONCEPT: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  SECTOR: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  RELATION: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
  AXIOM: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
}

const ROLE_STYLE: Record<string, string> = {
  CORE: 'bg-indigo-500/20 text-indigo-300',
  PERIPHERAL: 'bg-cyan-500/20 text-cyan-300',
  BRIDGE: 'bg-amber-500/20 text-amber-300',
  UNRESOLVED: 'bg-slate-500/20 text-slate-300',
}

function CardDetail({ card }: { card: ObjectCard }) {
  return (
    <Card className="bg-card/20 border-border hover:border-cyan-500/30 transition-colors h-full">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1">
            <CardTitle className="text-sm font-mono leading-tight">{card.name}</CardTitle>
            {card.path && (
              <div className="text-[9px] text-muted-foreground/60 font-mono mt-0.5 truncate">{card.path}</div>
            )}
          </div>
          <div className="flex flex-col gap-1 items-end shrink-0">
            <Badge variant="outline" className={`text-[9px] ${TYPE_STYLE[card.type] ?? 'bg-secondary'}`}>
              {card.type}
            </Badge>
            {card.orbital_role && (
              <span className={`text-[8px] px-1 rounded ${ROLE_STYLE[card.orbital_role] ?? ''}`}>
                {card.orbital_role}
              </span>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-2 text-xs">
        {card.description && (
          <p className="text-muted-foreground leading-relaxed">{card.description}</p>
        )}

        {/* Kepler / orbital metrics */}
        {(card.phi !== undefined || card.rho !== undefined || card.info_mass !== undefined) && (
          <div className="grid grid-cols-3 gap-1 text-[9px] font-mono">
            {card.phi !== undefined && (
              <div className="p-1 rounded bg-card/50 border border-border/50">
                <div className="text-muted-foreground/60">φ</div>
                <div>{card.phi.toFixed(3)}</div>
              </div>
            )}
            {card.rho !== undefined && (
              <div className="p-1 rounded bg-card/50 border border-border/50">
                <div className="text-muted-foreground/60">ρ</div>
                <div>{card.rho.toFixed(3)}</div>
              </div>
            )}
            {card.info_mass !== undefined && (
              <div className="p-1 rounded bg-card/50 border border-border/50">
                <div className="text-muted-foreground/60">M_info</div>
                <div>{card.info_mass.toFixed(3)}</div>
              </div>
            )}
            {card.berry_phase !== undefined && (
              <div className="p-1 rounded bg-card/50 border border-border/50">
                <div className="text-muted-foreground/60">Berry φ</div>
                <div>{card.berry_phase.toFixed(4)}</div>
              </div>
            )}
          </div>
        )}

        {/* W_ij connections */}
        {card.connections && card.connections.length > 0 && (
          <div className="space-y-1">
            <div className="text-[9px] text-muted-foreground/60 font-mono flex items-center gap-1">
              <Link2 className="w-3 h-3" /> W_ij nici ({card.connections.length})
            </div>
            <div className="space-y-0.5 max-h-20 overflow-auto">
              {card.connections.slice(0, 6).map((c, i) => (
                <div key={i} className="flex items-center gap-2 text-[8px] font-mono">
                  <span className="text-cyan-400/70 truncate w-24">{c.target.replace('ent_', '')}</span>
                  <div className="flex-1 h-1 rounded bg-card">
                    <div
                      className="h-full rounded bg-cyan-500"
                      style={{ width: `${Math.min(100, c.w * 100)}%` }}
                    />
                  </div>
                  <span className="text-muted-foreground w-8 text-right">{c.w.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tags */}
        {card.tags && card.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {card.tags.map((t) => (
              <span key={t} className="text-[9px] px-1.5 py-0.5 rounded bg-secondary text-secondary-foreground">
                {t}
              </span>
            ))}
          </div>
        )}

        {/* Dependencies */}
        {card.dependencies && card.dependencies.length > 0 && (
          <div className="text-[9px] font-mono text-muted-foreground/60">
            Deps: {card.dependencies.slice(0, 4).join(', ')}
            {card.dependencies.length > 4 && ` +${card.dependencies.length - 4}`}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default function Cards() {
  const [cards, setCards] = useState<ObjectCard[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Load from geometry/sectors (entities) + couplings for W_ij
    ;(async () => {
      const base = await getCIELBase()
      const [geo, mem] = await Promise.all([
        fetch(`${base}/api/geometry/sectors`).then((r) => r.json()),
        fetch(`${base}/api/orbital/memory`).then((r) => r.json()).catch(() => ({ records: [] })),
      ])

      {
        const nodeMap: Record<string, { src: string; dst: string; w: number }[]> = {}

        // Build W_ij adjacency list
        ;(geo.edges ?? []).forEach((e: { src: string; dst: string; w: number }) => {
          if (!nodeMap[e.src]) nodeMap[e.src] = []
          nodeMap[e.src].push({ src: e.src, dst: e.dst, w: e.w })
        })

        // Sector nodes → ENTITY/SECTOR cards
        const sectorCards: ObjectCard[] = (geo.nodes ?? []).map((n: any) => ({
          id: n.id,
          name: n.label || n.id,
          type: n.id.startsWith('ent_') ? 'ENTITY' : 'SECTOR',
          description: `Orbital type: ${n.orbital_type} · amplitude: ${n.amplitude?.toFixed(3)} · coherence: ${n.coherence_weight?.toFixed(3)}`,
          phi: n.phi,
          rho: n.rho ?? undefined,
          info_mass: n.info_mass,
          orbital_role: n.is_attractor ? 'CORE' : undefined,
          tags: [n.orbital_type],
          connections: (nodeMap[n.id] ?? []).map((e) => ({ target: e.dst, w: e.w })),
        }))

        // Memory records → additional cards
        const memCards: ObjectCard[] = ((mem.records ?? []) as any[]).slice(0, 30).map((r: any, i: number) => ({
          id: r.id ?? `mem_${i}`,
          name: r.path?.split('/').pop() ?? `Record ${i}`,
          type: 'MODULE',
          path: r.path,
          description: r.essence ?? r.summary ?? '',
          orbital_role: r.orbital_role,
          phi: r.phi,
          rho: r.confidence,
          berry_phase: r.berry_phase,
          tags: r.themes ?? [],
          connections: [],
        }))

        setCards([...sectorCards, ...memCards])
      }
    })()
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false))
  }, [])

  const types = ['all', ...Array.from(new Set(cards.map((c) => c.type)))]

  const filtered = cards.filter((c) => {
    const matchType = typeFilter === 'all' || c.type === typeFilter
    const q = search.toLowerCase()
    const matchSearch =
      !q ||
      c.name.toLowerCase().includes(q) ||
      (c.description ?? '').toLowerCase().includes(q) ||
      (c.tags ?? []).some((t) => t.toLowerCase().includes(q))
    return matchType && matchSearch
  })

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-5">
        <h1 className="text-2xl font-bold">Cards</h1>
        <p className="text-sm text-muted-foreground">
          Karty obiektów systemu — sektory, encje, moduły · nici W_ij · metryki Keplera
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-5">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Szukaj kart…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-card border border-border rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-cyan-500/50"
          />
        </div>
        <div className="flex flex-wrap gap-1 text-[10px] font-mono">
          {types.map((t) => (
            <button
              key={t}
              onClick={() => setTypeFilter(t)}
              className={`px-2 py-1 rounded border transition-colors ${
                typeFilter === t
                  ? 'border-cyan-500/40 bg-cyan-500/10 text-cyan-300'
                  : 'border-border text-muted-foreground'
              }`}
            >
              {t} {t === 'all' ? `(${cards.length})` : `(${cards.filter((c) => c.type === t).length})`}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-3 rounded border border-red-500/30 bg-red-500/10 text-xs font-mono text-red-300 mb-4">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-sm text-muted-foreground py-16 text-center">Ładowanie kart…</div>
      ) : (
        <ScrollArea className="h-[75vh]">
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 pr-2">
            {filtered.map((card) => (
              <CardDetail key={card.id} card={card} />
            ))}
            {filtered.length === 0 && (
              <div className="col-span-3 text-center text-muted-foreground py-16">
                Brak kart
              </div>
            )}
          </div>
        </ScrollArea>
      )}
    </div>
  )
}
