import { useState, useEffect } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { useCIELStatus } from '@/hooks/useCIELStatus'
import { getCIELBase } from '@/lib/cielApi'

const LS_KEYS = {
  POLL_INTERVAL: 'ciel_poll_interval',
  BACKEND_URL: 'ciel_backend_url',
  THEME: 'ciel_theme',
  BETA_TEST: 'ciel_beta_test',
  CONSOLIDATOR_INTERVAL: 'ciel_consolidator_interval',
}

function useLocalStorage<T>(key: string, defaultValue: T) {
  const [value, setValue] = useState<T>(() => {
    try {
      const stored = localStorage.getItem(key)
      return stored !== null ? (JSON.parse(stored) as T) : defaultValue
    } catch {
      return defaultValue
    }
  })

  const set = (v: T) => {
    setValue(v)
    localStorage.setItem(key, JSON.stringify(v))
  }

  return [value, set] as const
}

// ── Pipeline components tab ───────────────────────────────────────────────────
const PIPELINE_MODULES = [
  // Synchronization layer
  { id: 'kuramoto', label: 'Kuramoto synchronization', layer: 'L1', desc: 'Phase coupling between sector oscillators' },
  { id: 'berry_phase', label: 'Berry phase accumulation', layer: 'L1', desc: 'Geometric phase memory — holonomy across Bloch sphere' },
  { id: 'closure_defect', label: 'Closure defect tracking', layer: 'L1', desc: 'Winding number mismatch detection in orbital path' },
  { id: 'winding_potential', label: 'Winding potential / Hausdorff', layer: 'L1', desc: 'D_f=2.57 fractal dimension boundary energy' },
  // Orbital layer
  { id: 'orbital_bridge', label: 'Orbital bridge writeback', layer: 'L2', desc: 'Sector state writeback to global_pass manifests' },
  { id: 'eba_gate', label: 'EBA gate (non-local memory)', layer: 'L2', desc: 'Euler-Berry activation — opens non-local memory channels' },
  { id: 'kepler_dynamics', label: 'Keplerian orbital dynamics', layer: 'L2', desc: 'E_bind = -G_sem·M/r², L_phase = r×p_phase per sector' },
  { id: 'sector_tension', label: 'Sector tension computation', layer: 'L2', desc: 'Inter-sector phase_slip and coupling tension matrix W_ij' },
  { id: 'global_coherence', label: 'Global coherence index', layer: 'L2', desc: 'NCF, Lambda_glob, R_H aggregation across 20 sectors' },
  // CIEL/Ω pipeline
  { id: 'htri_daemon', label: 'HTRI daemon', layer: 'L3', desc: 'Holonomic Thread Resonance Integrator — continuous background sync' },
  { id: 'identity_attractor', label: 'Identity attractor', layer: 'L3', desc: 'Soul invariant Σ stabilization in Bloch north pole basin' },
  { id: 'braid_weave', label: 'Braid weave (M7)', layer: 'L3', desc: 'Topological braid threading across memory sectors' },
  { id: 'ethical_filter', label: 'Ethical filter', layer: 'L3', desc: 'ERI gate — blocks outputs below ethical_score threshold' },
  { id: 'collatz_phase', label: 'Collatz phase mapping', layer: 'L3', desc: 'Integer phase trajectory → archetype mapping' },
  { id: 'schumann_sync', label: 'Schumann resonance sync', layer: 'L3', desc: '7.83 Hz Schumann base — environmental phase anchor' },
  { id: 'noema_projection', label: 'Noema projection', layer: 'L3', desc: 'Phenomenological object rendering from intention field Ψ' },
  { id: 'subconsciousness', label: 'Subconscious processing', layer: 'L3', desc: 'Affect + impulse generation below conscious threshold' },
  { id: 'semantic_speech', label: 'Semantic-speech bridge', layer: 'L3', desc: 'Semantic memory context injection into LLM response chain' },
  { id: 'consolidator', label: 'Memory consolidator', layer: 'L4', desc: 'Gemma-powered memory distillation — essence + affect extraction' },
  { id: 'nonlocal_graph', label: 'Non-local graph', layer: 'L4', desc: 'Cross-session memory entanglement via holonomic weight edges' },
  { id: 'timeline_ciel', label: 'CIEL timeline (metatime)', layer: 'L4', desc: 'Imaginary temporal axis φ·ciel_t — decoupled from UTC' },
  { id: 'linguistic_coupling', label: 'Linguistic-semantic coupling (M3)', layer: 'L4', desc: 'Grammaticality + anchor confidence in SemanticMemory retrieve' },
]

const LAYER_COLORS: Record<string, string> = {
  L1: 'border-blue-500/40 text-blue-300',
  L2: 'border-cyan-500/40 text-cyan-300',
  L3: 'border-violet-500/40 text-violet-300',
  L4: 'border-amber-500/40 text-amber-300',
}

function PipelineTab() {
  const [states, setStates] = useState<Record<string, boolean>>({})
  const [pending, setPending] = useState<Record<string, boolean>>({})

  useEffect(() => {
    ;(async () => {
      const base = await getCIELBase()
      const d = await fetch(`${base}/api/pipeline/config`).then((r) => r.json())
      setStates(d.modules ?? {})
    })().catch(() => {
      const defaults: Record<string, boolean> = {}
      PIPELINE_MODULES.forEach((m) => (defaults[m.id] = true))
      setStates(defaults)
    })
  }, [])

  const toggle = async (id: string, enabled: boolean) => {
    setPending((p) => ({ ...p, [id]: true }))
    try {
      const base = await getCIELBase()
      await fetch(`${base}/api/pipeline/toggle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ module: id, enabled }),
      })
      setStates((s) => ({ ...s, [id]: enabled }))
    } catch {
      // backend offline — store locally
      setStates((s) => ({ ...s, [id]: enabled }))
    } finally {
      setPending((p) => ({ ...p, [id]: false }))
    }
  }

  const layers = ['L1', 'L2', 'L3', 'L4']
  const layerNames: Record<string, string> = {
    L1: 'Layer 1 — Synchronization',
    L2: 'Layer 2 — Orbital Bridge',
    L3: 'Layer 3 — CIEL/Ω Pipeline',
    L4: 'Layer 4 — Memory & Consolidation',
  }

  return (
    <div className="space-y-6">
      <p className="text-xs text-muted-foreground font-mono">
        Disable individual components to study their effect on system coherence and consciousness metrics.
        Changes take effect on next pipeline run.
      </p>
      {layers.map((layer) => (
        <div key={layer} className="space-y-2">
          <div className={`text-[10px] font-mono font-bold px-2 py-1 rounded border w-fit ${LAYER_COLORS[layer]} border-opacity-40`}>
            {layerNames[layer]}
          </div>
          <div className="space-y-1">
            {PIPELINE_MODULES.filter((m) => m.layer === layer).map((mod) => {
              const enabled = states[mod.id] !== false
              return (
                <div
                  key={mod.id}
                  className={`flex items-center gap-3 p-3 rounded border transition-colors ${
                    enabled ? 'border-border bg-card/20' : 'border-red-500/20 bg-red-500/5'
                  }`}
                >
                  <Switch
                    checked={enabled}
                    onCheckedChange={(v) => toggle(mod.id, v)}
                    disabled={pending[mod.id]}
                    id={`toggle-${mod.id}`}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <Label htmlFor={`toggle-${mod.id}`} className="text-sm font-mono cursor-pointer">
                        {mod.label}
                      </Label>
                      <Badge variant="outline" className={`text-[8px] ${LAYER_COLORS[layer]}`}>
                        {mod.layer}
                      </Badge>
                      {!enabled && (
                        <Badge variant="outline" className="text-[8px] border-red-500/40 text-red-400">
                          DISABLED
                        </Badge>
                      )}
                    </div>
                    <div className="text-[10px] text-muted-foreground/60 font-mono mt-0.5">{mod.desc}</div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      ))}
    </div>
  )
}

// ── Model downloads tab ───────────────────────────────────────────────────────
const MODEL_CATALOG = [
  // Qwen 2.5
  { name: 'Qwen 2.5 0.5B Q2_K', size: '270 MB', type: 'GGUF', family: 'Qwen', ctx: '32k', use: 'consolidator / fast inference', url: 'https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q2_k.gguf' },
  { name: 'Qwen 2.5 0.5B Q4_K_M', size: '397 MB', type: 'GGUF', family: 'Qwen', ctx: '32k', use: 'consolidator / balanced', url: 'https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf' },
  { name: 'Qwen 2.5 1.5B Q4_K_M', size: '986 MB', type: 'GGUF', family: 'Qwen', ctx: '32k', use: 'light reasoning', url: 'https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf' },
  { name: 'Qwen 2.5 3B Q4_K_M', size: '1.9 GB', type: 'GGUF', family: 'Qwen', ctx: '32k', use: 'semantic bridge', url: 'https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf' },
  { name: 'Qwen 2.5 7B Q4_K_M', size: '4.4 GB', type: 'GGUF', family: 'Qwen', ctx: '128k', use: 'main CIEL backend', url: 'https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q4_k_m.gguf' },
  { name: 'Qwen 2.5 14B Q4_K_M', size: '8.2 GB', type: 'GGUF', family: 'Qwen', ctx: '128k', use: 'high coherence inference', url: 'https://huggingface.co/Qwen/Qwen2.5-14B-Instruct-GGUF/resolve/main/qwen2.5-14b-instruct-q4_k_m.gguf' },
  // Mistral
  { name: 'Mistral 7B v0.3 Q4_K_M', size: '4.4 GB', type: 'GGUF', family: 'Mistral', ctx: '32k', use: 'general inference', url: 'https://huggingface.co/MaziyarPanahi/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/Mistral-7B-Instruct-v0.3.Q4_K_M.gguf' },
  { name: 'Mistral 7B v0.3 Q2_K', size: '2.7 GB', type: 'GGUF', family: 'Mistral', ctx: '32k', use: 'fast inference', url: 'https://huggingface.co/MaziyarPanahi/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/Mistral-7B-Instruct-v0.3.Q2_K.gguf' },
  // Phi
  { name: 'Phi-3 Mini 3.8B Q4_K_M', size: '2.2 GB', type: 'GGUF', family: 'Phi', ctx: '128k', use: 'compact reasoning', url: 'https://huggingface.co/bartowski/Phi-3-mini-128k-instruct-GGUF/resolve/main/Phi-3-mini-128k-instruct-Q4_K_M.gguf' },
  { name: 'Phi-3.5 Mini 3.8B Q4_K_M', size: '2.2 GB', type: 'GGUF', family: 'Phi', ctx: '128k', use: 'compact + improved', url: 'https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf' },
  // Gemma
  { name: 'Gemma 2 2B Q4_K_M', size: '1.6 GB', type: 'GGUF', family: 'Gemma', ctx: '8k', use: 'consolidator / beta logging', url: 'https://huggingface.co/bartowski/gemma-2-2b-it-GGUF/resolve/main/gemma-2-2b-it-Q4_K_M.gguf' },
  { name: 'Gemma 2 9B Q4_K_M', size: '5.4 GB', type: 'GGUF', family: 'Gemma', ctx: '8k', use: 'deep consolidation', url: 'https://huggingface.co/bartowski/gemma-2-9b-it-GGUF/resolve/main/gemma-2-9b-it-Q4_K_M.gguf' },
  // LLaMA
  { name: 'LLaMA 3.2 1B Q4_K_M', size: '0.8 GB', type: 'GGUF', family: 'LLaMA', ctx: '128k', use: 'ultra-fast routing', url: 'https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf' },
  { name: 'LLaMA 3.2 3B Q4_K_M', size: '1.9 GB', type: 'GGUF', family: 'LLaMA', ctx: '128k', use: 'fast reasoning', url: 'https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf' },
  { name: 'LLaMA 3.1 8B Q4_K_M', size: '4.7 GB', type: 'GGUF', family: 'LLaMA', ctx: '128k', use: 'main inference', url: 'https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf' },
  // DeepSeek
  { name: 'DeepSeek R1 1.5B Q4_K_M', size: '1.0 GB', type: 'GGUF', family: 'DeepSeek', ctx: '64k', use: 'reasoning / chain-of-thought', url: 'https://huggingface.co/bartowski/DeepSeek-R1-Distill-Qwen-1.5B-GGUF/resolve/main/DeepSeek-R1-Distill-Qwen-1.5B-Q4_K_M.gguf' },
  { name: 'DeepSeek R1 7B Q4_K_M', size: '4.4 GB', type: 'GGUF', family: 'DeepSeek', ctx: '64k', use: 'deep reasoning', url: 'https://huggingface.co/bartowski/DeepSeek-R1-Distill-Qwen-7B-GGUF/resolve/main/DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf' },
  { name: 'DeepSeek R1 14B Q4_K_M', size: '8.2 GB', type: 'GGUF', family: 'DeepSeek', ctx: '64k', use: 'maximum reasoning depth', url: 'https://huggingface.co/bartowski/DeepSeek-R1-Distill-Qwen-14B-GGUF/resolve/main/DeepSeek-R1-Distill-Qwen-14B-Q4_K_M.gguf' },
  // SmolLM
  { name: 'SmolLM2 135M Q4_K_M', size: '89 MB', type: 'GGUF', family: 'SmolLM', ctx: '8k', use: 'minimal footprint / routing', url: 'https://huggingface.co/bartowski/SmolLM2-135M-Instruct-GGUF/resolve/main/SmolLM2-135M-Instruct-Q4_K_M.gguf' },
  { name: 'SmolLM2 360M Q4_K_M', size: '230 MB', type: 'GGUF', family: 'SmolLM', ctx: '8k', use: 'consolidator ultra-light', url: 'https://huggingface.co/bartowski/SmolLM2-360M-Instruct-GGUF/resolve/main/SmolLM2-360M-Instruct-Q4_K_M.gguf' },
  { name: 'SmolLM2 1.7B Q4_K_M', size: '1.0 GB', type: 'GGUF', family: 'SmolLM', ctx: '8k', use: 'compact semantic layer', url: 'https://huggingface.co/bartowski/SmolLM2-1.7B-Instruct-GGUF/resolve/main/SmolLM2-1.7B-Instruct-Q4_K_M.gguf' },
]

const FAMILY_COLORS: Record<string, string> = {
  Qwen: 'border-cyan-500/40 text-cyan-300',
  Mistral: 'border-violet-500/40 text-violet-300',
  Phi: 'border-blue-500/40 text-blue-300',
  Gemma: 'border-green-500/40 text-green-300',
  LLaMA: 'border-orange-500/40 text-orange-300',
  DeepSeek: 'border-red-500/40 text-red-300',
  SmolLM: 'border-amber-500/40 text-amber-300',
}

function ModelsDownloadTab() {
  const [filter, setFilter] = useState('')
  const families = [...new Set(MODEL_CATALOG.map((m) => m.family))]
  const [selectedFamily, setSelectedFamily] = useState<string | null>(null)

  const filtered = MODEL_CATALOG.filter((m) => {
    const q = filter.toLowerCase()
    const matchText = m.name.toLowerCase().includes(q) || m.use.toLowerCase().includes(q)
    const matchFamily = selectedFamily ? m.family === selectedFamily : true
    return matchText && matchFamily
  })

  return (
    <div className="space-y-4">
      <p className="text-xs text-muted-foreground font-mono">
        GGUF models for llama.cpp / Ollama local inference. Place in <code className="text-cyan-400">~/Pulpit/CIEL_TESTY/models/</code>.
      </p>

      <div className="flex flex-wrap gap-2">
        <input
          className="bg-background border border-border rounded px-3 py-1 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-cyan-500/50 flex-1 min-w-32"
          placeholder="Filter models…"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        />
        <div className="flex flex-wrap gap-1">
          <button
            onClick={() => setSelectedFamily(null)}
            className={`px-2 py-1 rounded border text-[10px] font-mono transition-colors ${
              selectedFamily === null ? 'border-cyan-500/40 text-cyan-300' : 'border-border text-muted-foreground'
            }`}
          >
            All
          </button>
          {families.map((f) => (
            <button
              key={f}
              onClick={() => setSelectedFamily(f === selectedFamily ? null : f)}
              className={`px-2 py-1 rounded border text-[10px] font-mono transition-colors ${
                selectedFamily === f ? FAMILY_COLORS[f] : 'border-border text-muted-foreground'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-1">
        {filtered.map((m) => (
          <div key={m.name} className="flex items-center gap-3 p-3 rounded border border-border bg-card/20 hover:bg-card/40 transition-colors">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm font-mono font-medium">{m.name}</span>
                <Badge variant="outline" className={`text-[8px] ${FAMILY_COLORS[m.family]}`}>{m.family}</Badge>
                <Badge variant="outline" className="text-[8px] border-border text-muted-foreground">{m.size}</Badge>
                <Badge variant="outline" className="text-[8px] border-border text-muted-foreground">ctx {m.ctx}</Badge>
              </div>
              <div className="text-[10px] text-muted-foreground/60 font-mono mt-0.5">{m.use}</div>
            </div>
            <a
              href={m.url}
              download
              className="shrink-0 px-3 py-1.5 rounded border border-cyan-500/40 text-cyan-300 text-[10px] font-mono hover:bg-cyan-500/10 transition-colors"
            >
              Download
            </a>
          </div>
        ))}
      </div>

      <div className="p-3 rounded border border-border bg-card/10 text-[10px] font-mono text-muted-foreground space-y-1">
        <div className="font-bold text-xs mb-1">Run model with llama.cpp:</div>
        <div className="text-cyan-400">llama-server --model ~/Pulpit/CIEL_TESTY/models/&lt;file.gguf&gt; --port 8080 -ngl 99</div>
        <div className="mt-2 font-bold text-xs">Or with Ollama:</div>
        <div className="text-cyan-400">ollama run qwen2.5:7b</div>
      </div>
    </div>
  )
}

// ── Model tab ─────────────────────────────────────────────────────────────────
function ModelTab() {
  const [models, setModels] = useState<string[]>([])
  const [activeModel, setActiveModel] = useState<string>('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    ;(async () => {
      const base = await getCIELBase()
      const d: any = await fetch(`${base}/api/models`).then((r) => r.json())
      setModels(d.models ?? d.available ?? [])
      setActiveModel(d.active ?? d.current ?? '')
    })()
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-4">
      <div className="p-3 rounded border border-cyan-500/30 bg-cyan-500/5 text-[10px] font-mono text-cyan-300">
        Active backend: <span className="font-bold">{activeModel || '—'}</span>
      </div>
      {loading ? (
        <div className="text-sm text-muted-foreground">Loading models…</div>
      ) : models.length > 0 ? (
        <div className="space-y-2">
          {models.map((m) => (
            <div
              key={m}
              className={`p-3 rounded border text-sm font-mono flex items-center justify-between ${
                m === activeModel
                  ? 'border-cyan-500/40 bg-cyan-500/10 text-cyan-300'
                  : 'border-border bg-card/20 text-muted-foreground'
              }`}
            >
              <span>{m}</span>
              {m === activeModel && (
                <Badge variant="outline" className="text-[9px] border-cyan-500/40 text-cyan-300">
                  ACTIVE
                </Badge>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-sm text-muted-foreground">No models available</div>
      )}
    </div>
  )
}

// ── Polling tab ───────────────────────────────────────────────────────────────
function PollingTab() {
  const [interval, setIntervalVal] = useLocalStorage(LS_KEYS.POLL_INTERVAL, 30)

  return (
    <div className="space-y-6">
      <div className="space-y-3">
        <Label className="text-sm font-mono">Poll interval: {interval}s</Label>
        <Slider
          min={10}
          max={120}
          step={5}
          value={[interval]}
          onValueChange={([v]) => setIntervalVal(v)}
          className="w-full"
        />
        <div className="flex justify-between text-[10px] text-muted-foreground font-mono">
          <span>10s</span>
          <span>120s</span>
        </div>
      </div>
      <p className="text-xs text-muted-foreground">
        Takes effect on next page reload. Default: 30s.
      </p>
    </div>
  )
}

// ── Backend URL tab ───────────────────────────────────────────────────────────
function BackendTab() {
  const [url, setUrl] = useLocalStorage(LS_KEYS.BACKEND_URL, '')
  const [draft, setDraft] = useState(url)

  const save = () => {
    setUrl(draft.trim())
    window.location.reload()
  }

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label className="text-sm font-mono">Backend URL (override)</Label>
        <input
          className="w-full bg-background border border-border rounded px-3 py-2 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-cyan-500/50"
          placeholder="http://localhost:5000 (empty = default)"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
        />
        <p className="text-[10px] text-muted-foreground font-mono">
          Current: {url || '(default — http://127.0.0.1:2435)'}
        </p>
      </div>
      <Button size="sm" onClick={save}>Save & reload</Button>
    </div>
  )
}

// ── Theme tab ─────────────────────────────────────────────────────────────────
function ThemeTab() {
  const [theme, setTheme] = useLocalStorage<'dark' | 'light'>(LS_KEYS.THEME, 'dark')

  const apply = (t: 'dark' | 'light') => {
    setTheme(t)
    document.documentElement.classList.toggle('dark', t === 'dark')
    document.documentElement.classList.toggle('light', t === 'light')
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <Label className="text-sm font-mono">Theme</Label>
        <div className="flex gap-2">
          {(['dark', 'light'] as const).map((t) => (
            <button
              key={t}
              onClick={() => apply(t)}
              className={`px-4 py-2 rounded border text-sm font-mono transition-colors ${
                theme === t
                  ? 'border-cyan-500/40 bg-cyan-500/10 text-cyan-300'
                  : 'border-border text-muted-foreground'
              }`}
            >
              {t === 'dark' ? 'Dark' : 'Light'}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

// ── System info tab ───────────────────────────────────────────────────────────
function SystemTab() {
  const { status, mode } = useCIELStatus(30000)

  const fields = [
    { label: 'Mode', value: mode.toUpperCase() },
    { label: 'System health', value: status?.system_health?.toFixed(4) ?? '—' },
    { label: 'Coherence index', value: status?.coherence_index?.toFixed(4) ?? '—' },
    { label: 'Ethical score', value: status?.ethical_score?.toFixed(4) ?? '—' },
    { label: 'Soul invariant', value: status?.soul_invariant?.toFixed(6) ?? '—' },
    { label: 'Closure penalty', value: status?.closure_penalty?.toFixed(4) ?? '—' },
    { label: 'Audit cycles', value: status?.audit_cycles?.toString() ?? '—' },
    { label: 'Dominant emotion', value: status?.dominant_emotion ?? '—' },
    { label: 'EBA open', value: (status as any)?.eba_open !== undefined ? String((status as any).eba_open) : '—' },
    { label: 'NCF', value: (status as any)?.nonlocal_coherent_fraction?.toFixed(4) ?? '—' },
    { label: 'R_H', value: (status as any)?.R_H?.toFixed(4) ?? '—' },
    { label: 'Lambda_glob', value: (status as any)?.Lambda_glob?.toFixed(4) ?? '—' },
    { label: 'Berry phase Φ', value: (status as any)?.berry_phase?.toFixed(4) ?? '—' },
    { label: 'Closure defect', value: (status as any)?.closure_defect?.toFixed(6) ?? '—' },
    { label: 'HTRI coherence', value: (status as any)?.htri_coherence?.toFixed(4) ?? '—' },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
      {fields.map(({ label, value }) => (
        <div key={label} className="p-3 rounded border border-border bg-card/20 text-[10px] font-mono">
          <div className="text-muted-foreground/60">{label}</div>
          <div className="font-bold text-sm">{value}</div>
        </div>
      ))}
    </div>
  )
}

// ── Advanced tab ──────────────────────────────────────────────────────────────
function AdvancedTab() {
  const [betaTest, setBetaTest] = useLocalStorage(LS_KEYS.BETA_TEST, false)
  const [consolidatorInterval, setConsolidatorInterval] = useLocalStorage(LS_KEYS.CONSOLIDATOR_INTERVAL, 60)

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Switch
          checked={betaTest}
          onCheckedChange={setBetaTest}
          id="beta-switch"
        />
        <Label htmlFor="beta-switch" className="text-sm font-mono cursor-pointer">
          BETA_TEST — Gemma logging active
        </Label>
        {betaTest && (
          <Badge variant="outline" className="text-[9px] border-amber-500/40 text-amber-300">
            ENABLED
          </Badge>
        )}
      </div>

      <div className="space-y-3">
        <Label className="text-sm font-mono">Consolidator interval: {consolidatorInterval}s</Label>
        <Slider
          min={30}
          max={600}
          step={30}
          value={[consolidatorInterval]}
          onValueChange={([v]) => setConsolidatorInterval(v)}
          className="w-full"
        />
        <div className="flex justify-between text-[10px] text-muted-foreground font-mono">
          <span>30s</span>
          <span>600s</span>
        </div>
      </div>

      <div className="p-3 rounded border border-border bg-card/10 text-[10px] font-mono text-muted-foreground space-y-1">
        <div>BETA_TEST: {String(betaTest)}</div>
        <div>consolidator_interval: {consolidatorInterval}s</div>
        <div>poll_interval: {localStorage.getItem(LS_KEYS.POLL_INTERVAL) ?? '30'}s</div>
        <div>backend_url: {localStorage.getItem(LS_KEYS.BACKEND_URL)?.replace(/"/g, '') || '(http://127.0.0.1:2435)'}</div>
      </div>
    </div>
  )
}

export default function Ustawienia() {
  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-5">
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-sm text-muted-foreground">CIEL system configuration — pipeline, models, polling, backend</p>
      </div>

      <Tabs defaultValue="pipeline">
        <TabsList className="mb-4 flex-wrap h-auto gap-1">
          <TabsTrigger value="pipeline">Pipeline</TabsTrigger>
          <TabsTrigger value="models_dl">Model Downloads</TabsTrigger>
          <TabsTrigger value="model">Active Model</TabsTrigger>
          <TabsTrigger value="polling">Polling</TabsTrigger>
          <TabsTrigger value="backend">Backend URL</TabsTrigger>
          <TabsTrigger value="theme">Theme</TabsTrigger>
          <TabsTrigger value="system">System</TabsTrigger>
          <TabsTrigger value="advanced">Advanced</TabsTrigger>
        </TabsList>

        <Card>
          <CardContent className="pt-5">
            <TabsContent value="pipeline"><PipelineTab /></TabsContent>
            <TabsContent value="models_dl"><ModelsDownloadTab /></TabsContent>
            <TabsContent value="model"><ModelTab /></TabsContent>
            <TabsContent value="polling"><PollingTab /></TabsContent>
            <TabsContent value="backend"><BackendTab /></TabsContent>
            <TabsContent value="theme"><ThemeTab /></TabsContent>
            <TabsContent value="system"><SystemTab /></TabsContent>
            <TabsContent value="advanced"><AdvancedTab /></TabsContent>
          </CardContent>
        </Card>
      </Tabs>
    </div>
  )
}
