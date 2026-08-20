export function formatAnalysisDate(value?: string): string {
  if (!value) return "—"

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value

  const day = String(date.getDate()).padStart(2, "0")
  const month = String(date.getMonth() + 1).padStart(2, "0")
  const year = String(date.getFullYear()).slice(-2)
  const hours = String(date.getHours()).padStart(2, "0")
  const minutes = String(date.getMinutes()).padStart(2, "0")

  return `${day}/${month}/${year} - ${hours}:${minutes}`
}

export function formatConfidence(confidence?: number): string {
  if (confidence == null) return "0.0"
  return (Number(confidence) * 100).toFixed(1)
}
