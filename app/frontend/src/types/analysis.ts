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
