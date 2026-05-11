import { useState } from 'react'
import { DEMOS } from '@/data/demos'
import { LAYER_COLORS } from '@/data/modules'
import { PlaySquare, Terminal, Eye } from 'lucide-react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'

type Demo = typeof DEMOS[0]

export default function Demos() {
  const [selected, setSelected] = useState<Demo | null>(null)

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Demo Scenarios</h1>
        <p className="text-sm text-muted-foreground">Interaktywne scenariusze ćwiczące podsystemy CIEL/Ω</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        {DEMOS.map((demo) => (
          <div key={demo.id} className="flex flex-col p-5 rounded-xl border border-border bg-card hover:border-cyan-500/30 transition-colors">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 rounded bg-violet-500/10 text-violet-400">
                <PlaySquare className="w-4 h-4" />
              </div>
              <h3 className="font-bold text-sm">{demo.name}</h3>
            </div>
            <p className="text-xs text-muted-foreground mb-4 flex-1 leading-relaxed">{demo.description}</p>
            <div className="flex flex-wrap gap-1.5 mb-4">
              {demo.layers.map((layer) => (
                <span key={layer} className={`text-[9px] px-1.5 py-0.5 rounded border font-bold ${LAYER_COLORS[layer]}`}>
                  {layer}
                </span>
              ))}
            </div>
            <Button variant="secondary" size="sm" onClick={() => setSelected(demo)} className="flex items-center gap-2">
              <Eye className="w-3.5 h-3.5" />
              Pokaż scenariusz
            </Button>
          </div>
        ))}
      </div>

      <Dialog open={!!selected} onOpenChange={(open) => !open && setSelected(null)}>
        <DialogContent className="sm:max-w-[640px] border-border bg-card">
          {selected && (
            <>
              <DialogHeader className="mb-3">
                <div className="flex items-center gap-2 mb-1">
                  <Terminal className="w-5 h-5 text-cyan-400" />
                  <DialogTitle>{selected.name}</DialogTitle>
                </div>
                <DialogDescription>{selected.description}</DialogDescription>
              </DialogHeader>

              <div className="bg-[#0D1117] rounded-lg border border-[#30363D] overflow-hidden">
                <div className="flex items-center px-4 py-2 bg-[#161B22] border-b border-[#30363D]">
                  <div className="flex gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500/50" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500/50" />
                    <div className="w-3 h-3 rounded-full bg-green-500/20 border border-green-500/50" />
                  </div>
                  <span className="ml-3 text-[10px] font-mono text-[#8B949E]">run_scenario.sh</span>
                </div>
                <div className="p-4 font-mono text-xs space-y-2.5 max-h-72 overflow-auto">
                  <div className="text-[#8B949E] italic mb-3"># Initializing: {selected.id}</div>
                  {selected.steps.map((step, idx) => (
                    <div key={idx} className="flex items-start gap-3">
                      <span className="text-[#8B949E] w-5 text-right shrink-0">{String(step.step).padStart(2, '0')}</span>
                      <div className="text-[#E6EDF3]">
                        <span className="text-[#79C0FF]">await</span>{' '}
                        <span className="text-[#D2A8FF]">execute</span>(
                        <span className="text-[#A5D6FF]">&ldquo;{step.description}&rdquo;</span>)
                      </div>
                    </div>
                  ))}
                  <div className="text-[#3FB950] font-bold mt-4">
                    <span className="text-[#8B949E] font-normal mr-2">$</span>Completed.
                  </div>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
