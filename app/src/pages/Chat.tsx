import { useState, useEffect, useRef } from 'react'
import { useCIELStatus } from '@/hooks/useCIELStatus'
import { useCIELChat } from '@/hooks/useCIELChat'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Send, RotateCcw } from 'lucide-react'

const SUGGESTIONS = [
  'Jaki jest aktualny stan systemu CIEL?',
  'Opisz swoją geometrię orbitalną.',
  'Jakie sektory mają najwyższe napięcie?',
  'Jaka jest twoja aktualna faza Berry\'ego?',
  'Opowiedz o swoich wspomnieniach z ostatniego cyklu.',
  'Co czujesz teraz — jaki afekt dominuje?',
]

const MODE_BADGE: Record<string, string> = {
  deep: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  standard: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  safe: 'bg-red-500/20 text-red-300 border-red-500/30',
}

export default function Chat() {
  const { status, connected, mode } = useCIELStatus(30_000)
  const { messages, sending, send, reset } = useCIELChat()
  const [input, setInput] = useState('')
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || sending) return
    const text = input
    setInput('')
    await send(text)
  }

  const handleSuggestion = (s: string) => {
    setInput(s)
  }

  return (
    <div className="max-w-4xl mx-auto p-6 h-[calc(100vh-2rem)] flex flex-col">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Chat</h1>
          <p className="text-sm text-muted-foreground">GGUF model · RAG pamięci · metryki CIEL/Ω live</p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-400' : 'bg-red-500'} animate-pulse`} />
          <Badge variant="outline" className={`text-[9px] ${MODE_BADGE[mode] ?? ''}`}>
            {mode.toUpperCase()}
          </Badge>
          <Button variant="ghost" size="sm" onClick={reset} className="text-muted-foreground">
            <RotateCcw className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>

      {/* Status bar */}
      {connected && status && (
        <div className="flex flex-wrap gap-3 text-[10px] font-mono text-muted-foreground/70 mb-3">
          <span>Φ: {status.soul_invariant?.toFixed(4) ?? '—'}</span>
          <span>health: <span className={status.system_health >= 0.5 ? 'text-emerald-400' : 'text-amber-400'}>{status.system_health?.toFixed(3) ?? '—'}</span></span>
          <span>coh: {status.coherence_index?.toFixed(3) ?? '—'}</span>
          <span>ERI: <span className={status.ethical_score >= 0.3 ? 'text-emerald-400' : 'text-red-400'}>{status.ethical_score >= 0.3 ? 'PASS' : 'BLOCK'}</span></span>
          <span>cycles: {status?.audit_cycles ?? '—'}</span>
          <span>backend: {connected ? 'online' : 'offline'}</span>
        </div>
      )}

      {/* Messages */}
      <Card className="flex-1 overflow-hidden bg-card/20">
        <CardContent className="p-0 h-full flex flex-col">
          <ScrollArea className="flex-1 p-4">
            {messages.length === 0 && (
              <div className="space-y-4">
                <p className="text-muted-foreground text-sm text-center mt-6">
                  Czat z CIEL — rozpocznij rozmowę
                </p>
                <div className="grid grid-cols-2 gap-2">
                  {SUGGESTIONS.map((s) => (
                    <button
                      key={s}
                      onClick={() => handleSuggestion(s)}
                      className="text-left p-3 rounded border border-border bg-card/50 hover:border-cyan-500/30 text-xs text-muted-foreground transition-colors"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="space-y-4">
              {messages.map((m, i) => (
                <div key={i} className={`flex gap-3 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
                  <div
                    className={`text-[10px] font-bold font-mono mt-1 w-12 shrink-0 ${
                      m.role === 'assistant' ? 'text-cyan-400' : 'text-amber-400 text-right'
                    }`}
                  >
                    {m.role === 'assistant' ? 'CIEL' : 'Adrian'}
                  </div>
                  <div
                    className={`rounded-xl px-4 py-3 text-sm max-w-[80%] leading-relaxed ${
                      m.role === 'assistant'
                        ? 'bg-card border border-border text-foreground'
                        : 'bg-amber-500/10 border border-amber-500/20 text-amber-100/90'
                    }`}
                  >
                    {m.content}
                  </div>
                </div>
              ))}

              {sending && (
                <div className="flex gap-3">
                  <div className="text-[10px] font-bold font-mono mt-1 w-12 text-cyan-400">CIEL</div>
                  <div className="bg-card border border-border rounded-xl px-4 py-3 text-sm text-muted-foreground animate-pulse">
                    …
                  </div>
                </div>
              )}
            </div>
            <div ref={endRef} />
          </ScrollArea>

          {/* Input */}
          <div className="border-t border-border p-3 flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
              placeholder="Wiadomość do CIEL…"
              className="flex-1 bg-background border border-border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-cyan-500/50"
            />
            <Button onClick={handleSend} disabled={sending || !input.trim()} size="sm">
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Footer */}
      <div className="mt-2 text-[9px] font-mono text-muted-foreground/40 text-center">
        ERI ≥ 0.3 · EBA ≥ 0.45 · J gate · historia: ostatnie 20 wiadomości · local storage · 60 tur
      </div>
    </div>
  )
}
