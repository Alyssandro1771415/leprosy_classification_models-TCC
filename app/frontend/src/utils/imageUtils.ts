export function cleanBase64(raw: string): string {
  return raw.replace(/\s/g, "")
}

export function base64ToDataUrl(base64: string, mimeType = "image/png"): string {
  const clean = cleanBase64(base64)
  return clean ? `data:${mimeType};base64,${clean}` : ""
}

export function base64ToFile(base64: string, filename = "image.png"): File {
  const clean = cleanBase64(base64)
  const byteString = atob(clean)
  const buffer = new ArrayBuffer(byteString.length)
  const bytes = new Uint8Array(buffer)

  for (let i = 0; i < byteString.length; i++) {
    bytes[i] = byteString.charCodeAt(i)
  }

  return new File([buffer], filename, { type: "image/png" })
}

export function buildImageFormData(file: File): FormData {
  const formData = new FormData()
  formData.append("image", file)
  return formData
}
