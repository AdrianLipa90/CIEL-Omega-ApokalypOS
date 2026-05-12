import { useState } from 'react'
import { MODULES, LAYER_COLORS, type Layer } from '@/data/modules'
import { Badge } from '@/components/ui/badge'
import { ChevronRight, X, Layers, Network, Code2 } from 'lucide-react'

const LAYERS: Layer[] = [
  'Communication', 'LLM Backends', 'Core Physics', 'Emotion & CQCL',
  'Cognition', 'Ethics', 'Memory', 'LLM Runtime', 'Mathematics', 'Vocabulary', 'Bio & Sensing',
]

export default function Architecture() {
  const [active, setActive] = useState<Layer | null>(null)
  const mods = active ? MODULES.filter((m) => m.layer === active) : []

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Architecture Map</h1>
        <p className="text-sm text-muted-foreground">Interaktywna mapa warstw systemu CIEL/Ω — kliknij warstwę by zobaczyć moduły</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Layer list */}
        <div className="lg:w-1/3 space-y-2">
          {LAYERS.map((layer) => {
            const count = MODULES.filter((m) => m.layer === layer).length
            const isActive = active === layer
            return (
              <button
                key={layer}
                onClick={() => setActive(layer === active ? null : layer)}
                className={`w-full text-left p-4 rounded-xl border transition-colors ${
                  isActive ? 'border-cyan-500/40 bg-cyan-500/8' : 'border-border bg-card hover:border-border/80'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className={`font-semibold ${isActive ? 'text-cyan-300' : 'text-foreground'}`}>{layer}</div>
                    <div className="text-xs text-muted-foreground font-mono">{count} modułów</div>
                  </div>
                  <ChevronRight className={`w-4 h-4 transition-transform ${isActive ? 'rotate-90 text-cyan-400' : 'text-muted-foreground'}`} />
                </div>
              </button>
            )
          })}
        </div>

        {/* Module panel */}
        <div className="lg:w-2/3">
          {active ? (
            <div className="rounded-xl border border-border bg-card/50 p-6">
              <div className="flex items-center justify-between mb-4 pb-3 border-b border-border">
                <div className="flex items-center gap-2">
                  <Layers className="w-5 h-5 text-cyan-400" />
                  <h2 className="font-bold">{active}</h2>
                  <Badge className="text-[10px]">{mods.length}</Badge>
                </div>
                <button onClick={() => setActive(null)} className="p-1.5 hover:bg-muted rounded text-muted-foreground">
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {mods.map((mod) => (
                  <div key={mod.id} className="p-4 rounded-lg border border-border bg-background">
                    <div className="flex items-start justify-between mb-2">
                      <span className="font-semibold text-sm">{mod.name}</span>
                      <span className={`text-[9px] px-1.5 py-0.5 rounded border font-bold ${LAYER_COLORS[mod.layer]}`}>{mod.layer}</span>
                    </div>
                    <div className="flex items-center gap-1 text-[10px] font-mono text-muted-foreground bg-muted/50 px-2 py-1 rounded mb-2">
                      <Code2 className="w-3 h-3 shrink-0" />
                      <span className="truncate">{mod.path}</span>
                    </div>
                    <p className="text-xs text-muted-foreground leading-relaxed line-clamp-3">{mod.description}</p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="h-full min-h-64 flex items-center justify-center rounded-xl border border-dashed border-border bg-card/20">
              <div className="text-center text-muted-foreground">
                <Network className="w-10 h-10 mx-auto mb-3 opacity-20" />
                <p className="text-sm">Wybierz warstwę by zobaczyć moduły</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
