import { fetchWithTimeout, getApiBaseUrl } from "../config/api"
import { MODEL_VERSION } from "../types/analysis"
import { buildImageFormData } from "../utils/imageUtils"
import type { User } from "firebase/auth"

const headers = {
  "x-access-token": import.meta.env.VITE_SECRET_TOKEN,
}

export type PredictionResult = {
  detected: boolean
  prediction: string
  probability: number
  probabilityDisplay: string
}

export type FocusResult = {
  focusPreview: string
  preprocessedPreview?: string
}

export async function runPrediction(file: File): Promise<PredictionResult> {
  const response = await fetch(`${getApiBaseUrl()}/prediction_data`, {
    method: "POST",
    headers,
    body: buildImageFormData(file),
  })

  if (!response.ok) throw new Error(`Erro na predição: ${response.status}`)

  const data = await response.json()
  const isHanseniase = data.predicted_class !== "outro"

  return {
    detected: isHanseniase,
    prediction: isHanseniase ? "Hanseníase" : "Outro",
    probability: data.probability,
    probabilityDisplay: (data.probability * 100).toFixed(1),
  }
}

export async function fetchFocusMaps(file: File): Promise<FocusResult> {
  const response = await fetch(`${getApiBaseUrl()}/prediction_focus`, {
    method: "POST",
    headers,
    body: buildImageFormData(file),
  })

  if (!response.ok) throw new Error(`Erro ao gerar foco: ${response.status}`)

  const data = await response.json()
  const mimeType = data.mime_type ?? "image/png"

  return {
    focusPreview: `data:${mimeType};base64,${data.focus_base64}`,
    preprocessedPreview: data.preprocessed_base64
      ? `data:${mimeType};base64,${data.preprocessed_base64}`
      : undefined,
  }
}

export async function convertImageToBase64(file: File): Promise<string> {
  const response = await fetch(`${getApiBaseUrl()}/image/convert`, {
    method: "POST",
    headers,
    body: buildImageFormData(file),
  })

  if (!response.ok) throw new Error(`Erro na conversão: ${response.status}`)

  const data = await response.json()
  return data.base64
}

export async function ensureUserSynced(user: User): Promise<void> {
  const response = await fetchWithTimeout(`${getApiBaseUrl()}/users/consent/`, {
    method: "POST",
    headers: {
      ...headers,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_id: user.uid,
      email: user.email ?? "",
      name: user.displayName ?? "",
      allow: true,
    }),
  })

  if (!response.ok) {
    const data = await response.json().catch(() => null)
    throw new Error(data?.error ?? `Erro ao sincronizar usuário: ${response.status}`)
  }
}

export async function saveAnalysis(params: {
  user: User
  imageBase64: string
  prediction: string
  confidence: number
  allowForTraining: boolean
}) {
  if (!params.imageBase64) {
    throw new Error("Imagem da análise não encontrada")
  }

  await ensureUserSynced(params.user)

  const response = await fetchWithTimeout(`${getApiBaseUrl()}/predictions/save`, {
    method: "POST",
    headers: {
      ...headers,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_id: params.user.uid,
      image_base64: params.imageBase64,
      prediction: params.prediction,
      confidence: params.confidence,
      model_version: MODEL_VERSION,
      allow_for_training: params.allowForTraining,
    }),
  })

  if (!response.ok) {
    let message = `Erro ao salvar: ${response.status}`
    try {
      const data = await response.json()
      if (data?.error) message = data.error
    } catch {
      // mantém mensagem padrão
    }
    throw new Error(message)
  }
}

export async function deleteAnalysis(userId: string, predictionId: string) {
  const response = await fetch(
    `${getApiBaseUrl()}/predictions/${userId}/${predictionId}`,
    {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        "x-access-token": import.meta.env.VITE_SECRET_TOKEN,
      },
    },
  )

  if (!response.ok) {
    let message = `Erro ao deletar: ${response.status}`
    try {
      const data = await response.json()
      if (data?.error) message = data.error
    } catch {
      // mantém mensagem padrão
    }
    throw new Error(message)
  }
}
