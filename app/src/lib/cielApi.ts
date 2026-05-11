/**
 * CIEL API Connector
 * Łączy React app z Flask backend (domyślnie 127.0.0.1:2435).
 * Wszystkie endpointy CIEL dostępne jako typed functions
 */

const LS_BACKEND_URL_KEY = 'ciel_backend_url'

function normalizeBaseUrl(raw: string): string {
  const v = (raw || '').trim()
  // Prefer explicit IPv4 loopback by default; "localhost" can resolve to ::1
  // on some systems and fail if backend binds only 127.0.0.1.
  if (!v) return 'http://127.0.0.1:2435'
  return v.endsWith('/') ? v.slice(0, -1) : v
}

async function resolveBaseUrl(): Promise<string> {
  // 1) Tauri backend can supply the live port via get_ciel_base()
  try {
    // Lazy import so web builds don't choke.
    const mod = await import('@tauri-apps/api/core')
    const base = (await mod.invoke<string>('get_ciel_base')) || ''
    if (base.trim()) {
      const norm = normalizeBaseUrl(base)
      try {
        localStorage.setItem(LS_BACKEND_URL_KEY, norm)
      } catch {
        // ignore
      }
      return norm
    }
  } catch {
    // ignore
  }

  // 2) User override (web or non-tauri, or if tauri invoke failed)
  try {
    const ls = localStorage.getItem(LS_BACKEND_URL_KEY)
    if (ls) return normalizeBaseUrl(ls.replace(/"/g, ''))
  } catch {
    // ignore
  }

  // 3) Default
  return 'http://127.0.0.1:2435'
}

export async function getCIELBase(): Promise<string> {
  // Do not permanently cache: backend URL can appear a moment after app start
  // (Tauri spawns the backend and sets CIEL_API_URL asynchronously).
  return resolveBaseUrl()
}

export interface CIELStatus {
  system_mode: string
  backend_status: string
  coherence_index: number
  system_health: number
  closure_penalty: number
  ethical_score: number
  soul_invariant: number
  dominant_emotion: string
  energy_budget: string
  manifest_version: string
  satellite_authority: Record<string, unknown>
  audit_cycles?: number
  [key: string]: unknown
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatResponse {
  reply: string
  think?: string
  model?: string
}

export interface HunchEntry {
  ts: string
  hunch: string
  tags: string[]
  context: string
}

export interface ProjectEntry {
  id: string
  name: string
  status: 'active' | 'planned' | 'done' | 'paused'
  desc: string
  tags: string[]
  updated: string
}

// ── Core API ──────────────────────────────────────────────────────────────

export async function fetchStatus(): Promise<CIELStatus> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/api/status`)
  if (!r.ok) throw new Error(`status ${r.status}`)
  return r.json()
}

export async function fetchPanel(): Promise<Record<string, unknown>> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/api/panel`)
  if (!r.ok) throw new Error(`panel ${r.status}`)
  return r.json()
}

// ── Chat ──────────────────────────────────────────────────────────────────

export async function sendChatMessage(
  message: string,
  modelPath?: string
): Promise<ChatResponse> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/api/chat/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, model_path: modelPath }),
  })
  if (!r.ok) throw new Error(`chat ${r.status}`)
  return r.json()
}

export async function fetchChatHistory(): Promise<ChatMessage[]> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/api/chat/history`)
  if (!r.ok) throw new Error(`history ${r.status}`)
  const d = await r.json()
  return d.history || []
}

export async function resetChat(): Promise<void> {
  const base = await getCIELBase()
  await fetch(`${base}/api/chat/reset`, { method: 'POST' })
}

// ── Models ────────────────────────────────────────────────────────────────

export async function fetchModels(): Promise<{ path: string; name: string; size_gb: number }[]> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/api/models`)
  if (!r.ok) throw new Error(`models ${r.status}`)
  const d = await r.json()
  return d.models || []
}

// ── Pipeline ──────────────────────────────────────────────────────────────

export async function runPipeline(
  module: 'synchronize' | 'orbital_bridge' | 'ciel_pipeline'
): Promise<{ ok: boolean; stdout: string; returncode: number }> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/api/pipeline/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ module }),
  })
  if (!r.ok) throw new Error(`pipeline ${r.status}`)
  return r.json()
}

// ── Memory / Portal ───────────────────────────────────────────────────────

export async function addHunch(
  hunch: string,
  tags: string[],
  context?: string
): Promise<void> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/api/hunches/add`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ hunch, tags, context: context || '' }),
  })
  if (!r.ok) throw new Error(`hunch ${r.status}`)
}

export async function rebuildPortal(): Promise<{ ok: boolean; stdout: string }> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/api/portal/rebuild`, { method: 'POST' })
  if (!r.ok) throw new Error(`rebuild ${r.status}`)
  return r.json()
}

// ── Advisor ───────────────────────────────────────────────────────────────

export async function askAdvisor(question: string): Promise<string> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/portal/advisor`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ q: question }),
  })
  if (!r.ok) throw new Error(`advisor ${r.status}`)
  const d = await r.json()
  return d.answer || ''
}

// ── Connectivity check ────────────────────────────────────────────────────

export async function checkConnectivity(): Promise<boolean> {
  try {
    const base = await getCIELBase()
    await fetch(`${base}/api/status`, { signal: AbortSignal.timeout(2000) })
    return true
  } catch {
    return false
  }
}

// ── Projects ──────────────────────────────────────────────────────────────

export async function fetchProjects(): Promise<ProjectEntry[]> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/api/projects`)
  if (!r.ok) throw new Error(`projects ${r.status}`)
  const d = await r.json()
  return d.projects || []
}

export async function addProject(entry: Omit<ProjectEntry, 'id' | 'updated'>): Promise<void> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/api/projects/add`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(entry),
  })
  if (!r.ok) throw new Error(`projects/add ${r.status}`)
}

// ── Routines ──────────────────────────────────────────────────────────────

export interface RoutineSection { name: string; items: string[] }
export interface RoutinesData { sections: RoutineSection[]; last_updated: string }

export async function fetchRoutines(): Promise<RoutinesData> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/api/routines`)
  if (!r.ok) throw new Error(`routines ${r.status}`)
  return r.json()
}

// ── Constraints ───────────────────────────────────────────────────────────

export interface ConstraintEntry {
  id: string
  type: 'forbid' | 'obligate' | 'wish'
  text: string
  tags: string[]
  context: string
  ts: string
  source: string
}

export async function fetchConstraints(type?: string): Promise<ConstraintEntry[]> {
  const base = await getCIELBase()
  const url = type ? `${base}/api/constraints?type=${type}` : `${base}/api/constraints`
  const r = await fetch(url)
  if (!r.ok) throw new Error(`constraints ${r.status}`)
  const d = await r.json()
  return d.constraints || []
}

export async function addConstraint(entry: Pick<ConstraintEntry, 'type' | 'text' | 'tags' | 'context'>): Promise<void> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/api/constraints/add`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(entry),
  })
  if (!r.ok) throw new Error(`constraints/add ${r.status}`)
}

// ── Sub recent ────────────────────────────────────────────────────────────

export interface SubEntry {
  ts: string
  input: string
  output: string
  state: { dominant_emotion?: string; soul_invariant?: number; coherence_index?: number; ethical_score?: number; closure_penalty?: number }
}

export async function fetchSubRecent(n = 20): Promise<SubEntry[]> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/api/sub/recent?n=${n}`)
  if (!r.ok) throw new Error(`sub/recent ${r.status}`)
  const d = await r.json()
  return d.entries || []
}

// ── Consolidator results ──────────────────────────────────────────────────

export interface ConsolidatorResult {
  path: string
  status: string
  themes: string[]
  affect: string
  essence: string
  hunch: string
  processed_at: string
}

export async function fetchConsolidatorResults(): Promise<{ results: ConsolidatorResult[]; status: Record<string, unknown> }> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/api/consolidator/results`)
  if (!r.ok) throw new Error(`consolidator/results ${r.status}`)
  const d = await r.json()
  return {
    results: d.results || d || [],
    status: d.status || {},
  }
}

// ── Intentions ────────────────────────────────────────────────────────────

export interface IntentionEntry {
  id: string
  text: string
  priority: 'H' | 'M' | 'L'
  done: boolean
  ts: string
}

export async function fetchIntentions(): Promise<IntentionEntry[]> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/api/intentions`)
  if (!r.ok) throw new Error(`intentions ${r.status}`)
  const d = await r.json()
  return d.intentions || d.active || []
}

export async function addIntention(text: string, priority: 'H' | 'M' | 'L'): Promise<void> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/api/intentions/add`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, priority }),
  })
  if (!r.ok) throw new Error(`intentions/add ${r.status}`)
}

export async function markIntentionDone(id: string): Promise<void> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/api/intentions/done`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id }),
  })
  if (!r.ok) throw new Error(`intentions/done ${r.status}`)
}

// ── Dziennik ──────────────────────────────────────────────────────────────

export async function fetchDziennik(): Promise<string> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/api/dziennik`)
  if (!r.ok) throw new Error(`dziennik ${r.status}`)
  const d = await r.json()
  return d.text || ''
}

export async function appendDziennik(text: string): Promise<void> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/api/dziennik`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  if (!r.ok) throw new Error(`dziennik post ${r.status}`)
}

// ── Hunches (fetch, nie tylko add) ───────────────────────────────────────

export async function fetchHunches(): Promise<HunchEntry[]> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/api/hunches`)
  if (!r.ok) throw new Error(`hunches ${r.status}`)
  const d = await r.json()
  return d.hunches || d.entries || []
}

// ── Portal data ───────────────────────────────────────────────────────────

export async function fetchPortalData(): Promise<Record<string, unknown>> {
  const base = await getCIELBase()
  const r = await fetch(`${base}/api/portal/data`)
  if (!r.ok) throw new Error(`portal/data ${r.status}`)
  return r.json()
}

// ── Orbital memory ────────────────────────────────────────────────────────

export async function fetchOrbitalMemory(orbitClass?: string): Promise<{ records: unknown[]; counts: Record<string, number>; total: number }> {
  const base = await getCIELBase()
  const url = orbitClass
    ? `${base}/api/orbital/memory?class=${orbitClass}`
    : `${base}/api/orbital/memory`
  const r = await fetch(url)
  if (!r.ok) throw new Error(`orbital/memory ${r.status}`)
  return r.json()
}
