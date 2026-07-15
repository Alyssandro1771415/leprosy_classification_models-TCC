export type ConsentFlowState = {
  file: File
  preview: string
}

export type ResultFlowState = ConsentFlowState & {
  allowForTraining: boolean
  result: {
    detected: boolean
    prediction: string
    probability: number
    probabilityDisplay: string
  }
  preprocessedPreview?: string
  focusPreview: string
  imageBase64: string
}
