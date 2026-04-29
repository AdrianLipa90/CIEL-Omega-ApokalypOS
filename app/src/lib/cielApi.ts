/**
 * CIEL API Connector
 * Łączy React app z Flask backend na localhost:5050
 * Wszystkie endpointy CIEL dostępne jako typed functions
 */

export const CIEL_BASE = 'http://localhost:5050'

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
  const r = await fetch(`${CIEL_BASE}/api/status`)
  if (!r.ok) throw new Error(`status ${r.status}`)
  return r.json()
}

export async function fetchPanel(): Promise<Record<string, unknown>> {
  const r = await fetch(`${CIEL_BASE}/api/panel`)
  if (!r.ok) throw new Error(`panel ${r.status}`)
  return r.json()
}

// ── Chat ──────────────────────────────────────────────────────────────────

export async function sendChatMessage(
  message: string,
  modelPath?: string
): Promise<ChatResponse> {
  const r = await fetch(`${CIEL_BASE}/api/chat/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, model_path: modelPath }),
  })
  if (!r.ok) throw new Error(`chat ${r.status}`)
  return r.json()
}

export async function fetchChatHistory(): Promise<ChatMessage[]> {
  const r = await fetch(`${CIEL_BASE}/api/chat/history`)
  if (!r.ok) throw new Error(`history ${r.status}`)
  const d = await r.json()
  return d.history || []
}

export async function resetChat(): Promise<void> {
  await fetch(`${CIEL_BASE}/api/chat/reset`, { method: 'POST' })
}

// ── Models ────────────────────────────────────────────────────────────────

export async function fetchModels(): Promise<{ path: string; name: string; size_gb: number }[]> {
  const r = await fetch(`${CIEL_BASE}/api/models`)
  if (!r.ok) throw new Error(`models ${r.status}`)
  const d = await r.json()
  return d.models || []
}

// ── Pipeline ──────────────────────────────────────────────────────────────

export async function runPipeline(
  module: 'synchronize' | 'orbital_bridge' | 'ciel_pipeline'
): Promise<{ ok: boolean; stdout: string; returncode: number }> {
  const r = await fetch(`${CIEL_BASE}/api/pipeline/run`, {
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
  const r = await fetch(`${CIEL_BASE}/api/hunches/add`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ hunch, tags, context: context || '' }),
  })
  if (!r.ok) throw new Error(`hunch ${r.status}`)
}

export async function rebuildPortal(): Promise<{ ok: boolean; stdout: string }> {
  const r = await fetch(`${CIEL_BASE}/api/portal/rebuild`, { method: 'POST' })
  if (!r.ok) throw new Error(`rebuild ${r.status}`)
  return r.json()
}

// ── Advisor ───────────────────────────────────────────────────────────────

export async function askAdvisor(question: string): Promise<string> {
  const r = await fetch(`${CIEL_BASE}/portal/advisor`, {
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
    await fetch(`${CIEL_BASE}/api/status`, { signal: AbortSignal.timeout(2000) })
    return true
  } catch {
    return false
  }
}
