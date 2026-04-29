import { useState, useCallback } from 'react'
import { sendChatMessage, fetchChatHistory, resetChat, type ChatMessage } from '@/lib/cielApi'

interface UseCIELChatReturn {
  messages: ChatMessage[]
  sending: boolean
  error: string | null
  send: (text: string) => Promise<void>
  reset: () => Promise<void>
  loadHistory: () => Promise<void>
}

export function useCIELChat(): UseCIELChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const send = useCallback(async (text: string) => {
    if (!text.trim()) return
    setMessages(prev => [...prev, { role: 'user', content: text }])
    setSending(true)
    setError(null)
    try {
      const resp = await sendChatMessage(text)
      setMessages(prev => [...prev, { role: 'assistant', content: resp.reply }])
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'error'
      setError(msg)
      setMessages(prev => [...prev, { role: 'assistant', content: `[Błąd: ${msg}]` }])
    } finally {
      setSending(false)
    }
  }, [])

  const reset = useCallback(async () => {
    await resetChat()
    setMessages([])
    setError(null)
  }, [])

  const loadHistory = useCallback(async () => {
    try {
      const hist = await fetchChatHistory()
      setMessages(hist)
    } catch {}
  }, [])

  return { messages, sending, error, send, reset, loadHistory }
}
