import { Capacitor } from "@capacitor/core"

const API_TIMEOUT_MS = 15_000

export function getApiBaseUrl(): string {
  if (Capacitor.isNativePlatform()) {
    return (
      import.meta.env.VITE_API_LINK_MOBILE ||
      import.meta.env.VITE_API_LINK ||
      ""
    )
  }

  return import.meta.env.VITE_API_LINK || ""
}

export async function fetchWithTimeout(
  input: RequestInfo | URL,
  init?: RequestInit,
  timeoutMs = API_TIMEOUT_MS,
): Promise<Response> {
  const controller = new AbortController()
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs)

  try {
    return await fetch(input, {
      ...init,
      signal: controller.signal,
    })
  } finally {
    window.clearTimeout(timeoutId)
  }
}
