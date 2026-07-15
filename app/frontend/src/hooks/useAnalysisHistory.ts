import { useCallback, useEffect, useState } from "react"

import { fetchWithTimeout, getApiBaseUrl } from "../config/api"
import { useAuth } from "../contexts/AuthContext"
import type { HistoryItem } from "../types/analysis"

export function useAnalysisHistory() {
  const { user } = useAuth()
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchHistory = useCallback(async () => {
    if (!user?.uid) {
      setHistory([])
      setLoading(false)
      setError(null)
      return
    }

    try {
      setLoading(true)
      setError(null)

      const response = await fetchWithTimeout(
        `${getApiBaseUrl()}/predictions/history/${user.uid}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "x-access-token": import.meta.env.VITE_SECRET_TOKEN,
          },
        },
      )

      if (!response.ok) throw new Error(`Erro: ${response.status}`)

      const data = await response.json()

      if (data?.predictions) {
        setHistory(data.predictions)
      } else if (Array.isArray(data)) {
        setHistory(data)
      } else {
        setHistory([])
      }
    } catch (err) {
      const message =
        err instanceof DOMException && err.name === "AbortError"
          ? "Tempo esgotado ao conectar com o servidor."
          : "Não foi possível carregar o histórico."

      setError(message)
      setHistory([])
      console.error("Erro ao buscar histórico:", err)
    } finally {
      setLoading(false)
    }
  }, [user])

  useEffect(() => {
    fetchHistory()
  }, [fetchHistory])

  return { history, loading, error, refetch: fetchHistory }
}
