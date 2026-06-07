import axios from 'axios'

export const apiClient = axios.create({
  baseURL: '/api',
  timeout: 60_000,
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.response.use(
  (r) => r,
  (err) => {
    const msg = err.response?.data?.detail ?? err.message ?? 'Errore sconosciuto'
    return Promise.reject(new Error(msg))
  }
)

// Default workspace — overridable via context
export const DEFAULT_WORKSPACE = 'mio-studio'

/**
 * Invia una valutazione per una voce della cronologia.
 * Lancia Error('ALREADY_SUBMITTED') se il feedback è già stato inviato (HTTP 409).
 */
export async function submitFeedback(
  historyId: string,
  rating: number,
  tags: string[],
  note?: string,
): Promise<void> {
  const res = await fetch(`/api/history/${historyId}/feedback`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rating, tags, note: note ?? null }),
  })
  if (res.status === 409) throw new Error('ALREADY_SUBMITTED')
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
}
