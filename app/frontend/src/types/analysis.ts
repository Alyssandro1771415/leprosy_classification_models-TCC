export const MODEL_VERSION = "v2.0-y-bilateral"

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

export type FocusResponse = {
  focus_base64: string
  preprocessed_base64?: string
  mime_type?: string
}
