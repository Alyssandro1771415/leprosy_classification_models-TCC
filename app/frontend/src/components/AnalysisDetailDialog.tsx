import {
  Badge,
  Box,
  Dialog,
  Grid,
  Heading,
  Portal,
  Separator,
  Spinner,
  Stack,
  Text,
} from "@chakra-ui/react"
import { useEffect, useState } from "react"
import AnalysisImagePair from "./AnalysisImagePair"
import type { HistoryItem } from "../types/analysis"
import { base64ToDataUrl, base64ToFile, buildImageFormData } from "../utils/imageUtils"

type AnalysisDetailDialogProps = {
  item: HistoryItem | null
  open: boolean
  onClose: () => void
}

function formatDate(value?: string): string {
  if (!value) return "—"
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString("pt-BR")
}

function formatConfidence(confidence?: number): string {
  if (confidence == null) return "—"
  return `${(Number(confidence) * 100).toFixed(1)}%`
}

export default function AnalysisDetailDialog({
  item,
  open,
  onClose,
}: AnalysisDetailDialogProps) {
  const [focusPreview, setFocusPreview] = useState<string | null>(null)
  const [preprocessedPreview, setPreprocessedPreview] = useState<string | null>(null)
  const [loadingFocus, setLoadingFocus] = useState(false)
  const [focusError, setFocusError] = useState<string | null>(null)

  const originalSrc = item?.imageBase64
    ? base64ToDataUrl(item.imageBase64)
    : ""

  useEffect(() => {
    if (!open || !item?.imageBase64) {
      setFocusPreview(null)
      setPreprocessedPreview(null)
      setFocusError(null)
      setLoadingFocus(false)
      return
    }

    let cancelled = false

    async function fetchFocus() {
      try {
        setLoadingFocus(true)
        setFocusError(null)
        setFocusPreview(null)
        setPreprocessedPreview(null)

        const file = base64ToFile(item!.imageBase64!, `analysis-${item!.id ?? "detail"}.png`)
        const response = await fetch(`${import.meta.env.VITE_API_LINK}/prediction_focus`, {
          method: "POST",
          headers: {
            "x-access-token": import.meta.env.VITE_SECRET_TOKEN,
          },
          body: buildImageFormData(file),
        })

        if (!response.ok) {
          throw new Error(`Erro ao gerar mapa de calor: ${response.status}`)
        }

        const data = await response.json()
        const mimeType = data.mime_type ?? "image/png"
        const preview = `data:${mimeType};base64,${data.focus_base64}`
        const preprocessed = data.preprocessed_base64
          ? `data:${mimeType};base64,${data.preprocessed_base64}`
          : null

        if (!cancelled) {
          setFocusPreview(preview)
          setPreprocessedPreview(preprocessed)
        }
      } catch (error) {
        if (!cancelled) {
          console.error("Erro ao buscar mapa de calor:", error)
          setFocusError("Não foi possível gerar o mapa de calor para esta análise.")
        }
      } finally {
        if (!cancelled) {
          setLoadingFocus(false)
        }
      }
    }

    fetchFocus()

    return () => {
      cancelled = true
    }
  }, [open, item])

  const isHanseniase = item?.prediction === "Hanseníase"

  return (
    <Dialog.Root
      open={open}
      onOpenChange={(details) => {
        if (!details.open) onClose()
      }}
      size="xl"
    >
      <Portal>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content borderRadius="2xl" maxW="5xl" maxH="90vh" overflowY="auto">
            <Dialog.Header>
              <Dialog.Title>Detalhes da Análise</Dialog.Title>
              <Dialog.CloseTrigger />
            </Dialog.Header>

            <Dialog.Body pb={6}>
              {!item ? null : (
                <Stack gap={6}>
                  <Box
                    p={4}
                    borderRadius="md"
                    bg={isHanseniase ? "red.500" : "green.500"}
                    color="white"
                  >
                    <Text fontWeight="bold" fontSize="lg">
                      Predição: {item.prediction ?? "—"}
                    </Text>
                    <Text>Confiança: {formatConfidence(item.confidence)}</Text>
                  </Box>

                  <Box>
                    <Heading size="sm" mb={3}>
                      Informações
                    </Heading>
                    <Grid templateColumns={{ base: "1fr", md: "repeat(2, 1fr)" }} gap={3}>
                      <InfoRow label="Data da análise" value={formatDate(item.createdAt)} />
                      <InfoRow
                        label="Uso para treinamento"
                        value={item.allowForTraining ? "Autorizado" : "Não autorizado"}
                      />
                      {item.id && <InfoRow label="ID do registro" value={item.id} />}
                    </Grid>
                  </Box>

                  <Separator />

                  <Box>
                    <Heading size="sm" mb={2}>
                      Visualização para o profissional de saúde
                    </Heading>
                    <Text color="gray.500" fontSize="sm" mb={4}>
                      Visualização em três etapas: imagem original, resultado do pré-processamento
                      (canal Y + filtro bilateral) e mapa de calor Grad-CAM sobre a entrada do modelo.
                    </Text>

                    {loadingFocus && !focusPreview ? (
                      <Stack align="center" py={10} gap={3}>
                        <Spinner size="lg" color="teal.500" />
                        <Text color="gray.500" fontSize="sm">
                          Gerando mapa de calor...
                        </Text>
                      </Stack>
                    ) : (
                      <AnalysisImagePair
                        originalSrc={originalSrc}
                        preprocessedSrc={preprocessedPreview}
                        focusSrc={focusPreview}
                        loadingFocus={loadingFocus}
                      />
                    )}

                    {focusError && (
                      <Text color="red.500" fontSize="sm" mt={3}>
                        {focusError}
                      </Text>
                    )}
                  </Box>

                  <Badge colorScheme="teal" w="fit-content">
                    Grad-CAM — explicação visual da predição
                  </Badge>
                </Stack>
              )}
            </Dialog.Body>
          </Dialog.Content>
        </Dialog.Positioner>
      </Portal>
    </Dialog.Root>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <Box p={3} borderRadius="md" border="1px solid" borderColor="gray.200">
      <Text fontSize="xs" color="gray.500" mb={1}>
        {label}
      </Text>
      <Text fontSize="sm" fontWeight="medium" wordBreak="break-all">
        {value}
      </Text>
    </Box>
  )
}
