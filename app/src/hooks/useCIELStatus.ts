import { useState, useEffect, useCallback } from 'react'
import { fetchStatus, checkConnectivity, type CIELStatus } from '@/lib/cielApi'

interface UseCIELStatusReturn {
  status: CIELStatus | null
  connected: boolean
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
  mode: 'deep' | 'standard' | 'safe'
}

const DEFAULT_STATUS: CIELStatus = {
  system_mode: 'offline',
  backend_status: 'offline',
  coherence_index: 0,
  system_health: 0,
  closure_penalty: 0,
  ethical_score: 0,
  soul_invariant: 0,
  dominant_emotion: '—',
  energy_budget: '—',
  manifest_version: '—',
  satellite_authority: {},
}

export function useCIELStatus(pollIntervalMs = 30_000): UseCIELStatusReturn {
  const [status, setStatus] = useState<CIELStatus | null>(null)
  const [connected, setConnected] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    try {
      const alive = await checkConnectivity()
      setConnected(alive)
      if (!alive) {
        setError('CIEL backend offline')
        setLoading(false)
        return
      }
      const data = await fetchStatus()
      setStatus(data)
      setError(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'unknown error')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
    const id = setInterval(refresh, pollIntervalMs)
    return () => clearInterval(id)
  }, [refresh, pollIntervalMs])

  const closure = status?.closure_penalty ?? 0
  const mode = closure < 5.2 ? 'deep' : closure < 5.8 ? 'standard' : 'safe'

  return { status: status ?? DEFAULT_STATUS, connected, loading, error, refresh, mode }
}
