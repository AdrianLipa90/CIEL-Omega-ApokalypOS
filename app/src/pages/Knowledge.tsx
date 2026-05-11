import { useState } from 'react'
import { CONCEPTS } from '@/data/concepts'
import { Search, BookOpen, Hash } from 'lucide-react'

export default function Knowledge() {
  const [search, setSearch] = useState('')

  const filtered = CONCEPTS.filter(
    (c) =>
      c.title.toLowerCase().includes(search.toLowerCase()) ||
      c.description.toLowerCase().includes(search.toLowerCase()),
  )

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
          <BookOpen className="w-5 h-5 text-cyan-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">Knowledge Panel</h1>
          <p className="text-sm text-muted-foreground">Pojęcia, formuły i definicje architektury CIEL/Ω</p>
        </div>
      </div>

      <div className="relative max-w-xl">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <input
          type="text"
          placeholder="Szukaj pojęć, formuł, warstw…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2.5 bg-card border border-border rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-cyan-500/50"
        />
      </div>

      <div className="space-y-4">
        {filtered.map((concept) => (
          <div
            key={concept.id}
            className="p-5 rounded-xl border border-border bg-card hover:border-cyan-500/30 transition-colors group"
          >
            <div className="flex items-start justify-between mb-3">
              <h3 className="font-bold flex items-center gap-2">
                <Hash className="w-4 h-4 text-cyan-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                {concept.title}
              </h3>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-secondary text-secondary-foreground font-medium uppercase tracking-wider shrink-0 ml-2">
                {concept.category}
              </span>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">{concept.description}</p>
            {concept.formula && (
              <pre className="mt-3 p-3 rounded bg-[#0D1117] border border-[#30363D] text-[#79C0FF] text-xs font-mono whitespace-pre-wrap overflow-x-auto">
                {concept.formula}
              </pre>
            )}
          </div>
        ))}

        {filtered.length === 0 && (
          <div className="text-center py-16 text-muted-foreground border border-dashed border-border rounded-xl bg-card/20">
            <p>Brak wyników dla &ldquo;{search}&rdquo;</p>
          </div>
        )}
      </div>
    </div>
  )
}
