export type HistoryItem = {
  id?: string
  imageBase64?: string
  prediction?: string
  confidence?: number
  createdAt?: string
  modelVersion?: string | null
  allowForTraining?: boolean
}

export type AnalyzeResult = {
  detected: boolean
  probability: string
}
