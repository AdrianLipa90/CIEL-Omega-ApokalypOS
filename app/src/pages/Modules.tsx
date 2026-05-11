import { useState } from 'react'
import { MODULES, LAYER_COLORS, type Layer } from '@/data/modules'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Search, Code2 } from 'lucide-react'

const ALL_LAYERS = Array.from(new Set(MODULES.map((m) => m.layer))) as Layer[]

export default function Modules() {
  const [search, setSearch] = useState('')
  const [layerFilter, setLayerFilter] = useState<Layer | 'all'>('all')

  const filtered = MODULES.filter((m) => {
    const q = search.toLowerCase()
    const matchLayer = layerFilter === 'all' || m.layer === layerFilter
    const matchSearch =
      !q ||
      m.name.toLowerCase().includes(q) ||
      m.path.toLowerCase().includes(q) ||
      m.description.toLowerCase().includes(q)
    return matchLayer && matchSearch
  })

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-5">
      <div>
        <h1 className="text-2xl font-bold">Modules</h1>
        <p className="text-sm text-muted-foreground">
          Wszystkie moduły systemu CIEL/Ω — {MODULES.length} modułów w {ALL_LAYERS.length} warstwach
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Szukaj modułów…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10 pr-4 py-2 bg-card border border-border rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-cyan-500/50 w-full"
          />
        </div>
        <div className="flex flex-wrap gap-1 text-[10px] font-mono">
          <button
            onClick={() => setLayerFilter('all')}
            className={`px-2 py-1 rounded border transition-colors ${
              layerFilter === 'all'
                ? 'border-cyan-500/40 bg-cyan-500/10 text-cyan-300'
                : 'border-border text-muted-foreground'
            }`}
          >
            Wszystkie ({MODULES.length})
          </button>
          {ALL_LAYERS.map((layer) => {
            const count = MODULES.filter((m) => m.layer === layer).length
            return (
              <button
                key={layer}
                onClick={() => setLayerFilter(layer)}
                className={`px-2 py-1 rounded border transition-colors ${
                  layerFilter === layer
                    ? `${LAYER_COLORS[layer]} border-current`
                    : 'border-border text-muted-foreground'
                }`}
              >
                {layer.split(' ')[0]} ({count})
              </button>
            )
          })}
        </div>
      </div>

      {/* Results count */}
      <div className="text-[10px] font-mono text-muted-foreground/60">
        {filtered.length} modułów
      </div>

      {/* Module grid */}
      <ScrollArea className="h-[68vh]">
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 pr-2">
          {filtered.map((mod) => (
            <div key={mod.id} className="p-4 rounded-lg border border-border bg-card/20 hover:border-cyan-500/20 transition-colors">
              <div className="flex items-start justify-between mb-2 gap-2">
                <span className="font-semibold text-sm leading-tight">{mod.name}</span>
                <Badge
                  variant="outline"
                  className={`text-[8px] shrink-0 ${LAYER_COLORS[mod.layer]}`}
                >
                  {mod.layer.split(' ').slice(0, 2).join(' ')}
                </Badge>
              </div>
              <div className="flex items-center gap-1 text-[9px] font-mono text-muted-foreground bg-muted/40 px-2 py-1 rounded mb-2">
                <Code2 className="w-3 h-3 shrink-0" />
                <span className="truncate">{mod.path}</span>
              </div>
              <p className="text-[10px] text-muted-foreground leading-relaxed line-clamp-3">
                {mod.description}
              </p>
            </div>
          ))}
          {filtered.length === 0 && (
            <div className="col-span-3 text-center text-muted-foreground py-16">
              Brak modułów dla wybranych filtrów
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  )
}
