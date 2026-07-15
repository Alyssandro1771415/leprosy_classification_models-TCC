import {
  Box,
  Button,
  Container,
  Heading,
  Image,
  Stack,
  Text,
  Spinner,
  Separator,
  Grid,
  Badge,
} from "@chakra-ui/react"
import { useState, useEffect, useCallback } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import AnalysisDetailDialog from "../../components/AnalysisDetailDialog"
import { useAuth } from "../../contexts/AuthContext"
import type { HistoryItem } from "../../types/analysis"
import { MODEL_VERSION } from "../../types/analysis"
import { getApiBaseUrl } from "../../config/api"
import { base64ToDataUrl, buildImageFormData } from "../../utils/imageUtils"

export default function Analyze() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const { user } = useAuth()

  const image = state?.preview as string | undefined
  const file = state?.file as File | undefined

  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [selectedItem, setSelectedItem] = useState<HistoryItem | null>(null)
  const [detailOpen, setDetailOpen] = useState(false)

  // Estado para o consentimento
  const [allowForTraining, setAllowForTraining] = useState("false")

  const fetchHistory = useCallback(async () => {
    if (!user?.uid) return

    try {
      setLoadingHistory(true)
      const response = await fetch(
        `${getApiBaseUrl()}/predictions/history/${user.uid}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "x-access-token": import.meta.env.VITE_SECRET_TOKEN
        }
      }
      )

      if (!response.ok) throw new Error(`Erro: ${response.status}`)

      const data = await response.json()

      if (data && data.predictions) {
        setHistory(data.predictions)
      } else if (Array.isArray(data)) {
        setHistory(data)
      }
    } catch (error) {
      console.error("Erro ao buscar histórico:", error)
    } finally {
      setLoadingHistory(false)
    }
  }, [user])

  useEffect(() => {
    fetchHistory()
  }, [fetchHistory])

  async function handleAnalyze() {
    if (!file || !user) return

    try {
      setLoading(true)

      const predRes = await fetch(`${getApiBaseUrl()}/prediction_data`, {
        method: "POST",
        headers: {
          "x-access-token": import.meta.env.VITE_SECRET_TOKEN
        },
        body: buildImageFormData(file),
      })
      const predData = await predRes.json()
      const isHanseniase = predData.predicted_class !== "outro"

      const convRes = await fetch(`${getApiBaseUrl()}/image/convert`, {
        method: "POST",
        headers: {
          "x-access-token": import.meta.env.VITE_SECRET_TOKEN
        },
        body: buildImageFormData(file),
      })
      const convData = await convRes.json()

      const saveRes = await fetch(`${getApiBaseUrl()}/predictions/save`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-access-token": import.meta.env.VITE_SECRET_TOKEN
        },
        body: JSON.stringify({
          user_id: user.uid,
          image_base64: convData.base64,
          prediction: isHanseniase ? "Hanseníase" : "Outro",
          confidence: predData.probability,
          model_version: MODEL_VERSION,
          allow_for_training: allowForTraining === "true"
        }),
      })

      if (saveRes.ok) {
        const nextResult = {
          detected: isHanseniase,
          probability: (predData.probability * 100).toFixed(2)
        }

        setResult(nextResult)
        fetchHistory()

        const focusRes = await fetch(`${getApiBaseUrl()}/prediction_focus`, {
          method: "POST",
          headers: {
            "x-access-token": import.meta.env.VITE_SECRET_TOKEN
          },
          body: buildImageFormData(file),
        })

        if (!focusRes.ok) throw new Error(`Erro ao gerar foco do modelo: ${focusRes.status}`)

        const focusData = await focusRes.json()
        const mimeType = focusData.mime_type ?? "image/png"
        const focusPreview = `data:${mimeType};base64,${focusData.focus_base64}`
        const preprocessedPreview = focusData.preprocessed_base64
          ? `data:${mimeType};base64,${focusData.preprocessed_base64}`
          : undefined

        navigate("/analyze/focus", {
          state: {
            preview: image,
            preprocessedPreview,
            focusPreview,
            result: nextResult,
          },
        })
      }
    } catch (error) {
      console.error(error)
      alert("Erro no processamento")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container py={8} maxW="4xl">
      <Stack gap={8}>
        {image && (
          <Box borderBottom="1px solid" borderColor="gray.100" pb={8}>
            <Heading size="md" mb={4}>Nova Análise</Heading>
            <Grid templateColumns={{ base: "1fr", md: "1fr 1fr" }} gap={6}>
              <Image src={image} borderRadius="lg" objectFit="cover" h="300px" />
              <Stack justify="center" gap={4}>

                {/* Seção de Consentimento - Sem fundo e texto cinza claro negrito */}
                <Box py={2}>
                  <Text fontSize="sm" mb={4} fontWeight="bold" color="gray.400" lineHeight="tall">
                    Permito o uso da seguinte imagem para uso posterior de treinamento e aprimoramento da inteligência artificial responsável pelo diagnóstico neste app.
                  </Text>

                  <Stack direction="row" gap={8}>
                    <Box as="label" display="flex" alignItems="center" gap={2} cursor="pointer">
                      <input
                        type="radio"
                        name="allowForTraining"
                        value="true"
                        checked={allowForTraining === "true"}
                        onChange={(e) => setAllowForTraining(e.target.value)}
                        style={{
                          cursor: "pointer",
                          accentColor: "#319795",
                          width: "18px",
                          height: "18px"
                        }}
                      />
                      <Text fontSize="md" fontWeight="bold" color="gray.400">Sim</Text>
                    </Box>

                    <Box as="label" display="flex" alignItems="center" gap={2} cursor="pointer">
                      <input
                        type="radio"
                        name="allowForTraining"
                        value="false"
                        checked={allowForTraining === "false"}
                        onChange={(e) => setAllowForTraining(e.target.value)}
                        style={{
                          cursor: "pointer",
                          accentColor: "#319795",
                          width: "18px",
                          height: "18px"
                        }}
                      />
                      <Text fontSize="md" fontWeight="bold" color="gray.400">Não</Text>
                    </Box>
                  </Stack>
                </Box>

                <Button
                  colorScheme="teal"
                  size="lg"
                  onClick={handleAnalyze}
                  loading={loading}
                  disabled={!!result}
                >
                  Realizar Diagnóstico
                </Button>

                {result && (
                  <Box p={4} borderRadius="md" bg={result.detected ? "red.500" : "green.500"} color="white">
                    <Text fontWeight="bold">Predição: {result.detected ? "Hanseníase" : "Não Detectado"}</Text>
                    <Text>Confiança: {result.probability}%</Text>
                  </Box>
                )}
              </Stack>
            </Grid>
          </Box>
        )}

        <Box>
          <Heading size="md" mb={4}>Histórico Recente</Heading>
          <Separator mb={6} />

          {loadingHistory ? (
            <Spinner size="xl" />
          ) : (
            <Grid templateColumns={{ base: "1fr", md: "repeat(3, 1fr)" }} gap={4}>
              {history.map((item, index) => {
                const imageSrc = item.imageBase64
                  ? base64ToDataUrl(item.imageBase64)
                  : "https://via.placeholder.com/150"

                return (
                  <Box
                    key={item.id ?? index}
                    p={3}
                    borderRadius="lg"
                    border="1px solid"
                    borderColor="gray.200"
                    cursor="pointer"
                    transition="all 0.2s"
                    _hover={{
                      borderColor: "teal.400",
                      boxShadow: "md",
                      transform: "translateY(-2px)",
                    }}
                    onClick={() => {
                      setSelectedItem(item)
                      setDetailOpen(true)
                    }}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault()
                        setSelectedItem(item)
                        setDetailOpen(true)
                      }
                    }}
                  >
                    <Image
                      src={imageSrc}
                      borderRadius="md"
                      h="150px"
                      w="100%"
                      style={{ objectFit: "cover" }}
                      mb={2}
                      onError={(e) => {
                        (e.target as HTMLImageElement).src = "https://via.placeholder.com/150"
                      }}
                    />
                    <Badge colorScheme={item.prediction === "Hanseníase" ? "red" : "green"}>
                      {item.prediction}
                    </Badge>
                    <Text fontSize="xs" fontWeight="bold" mt={1}>
                      Confiança: {item.confidence ? (Number(item.confidence) * 100).toFixed(1) : "0.0"}%
                    </Text>
                    <Text fontSize="xs" color="teal.600" mt={2}>
                      Toque para ver detalhes e mapa de calor
                    </Text>
                  </Box>
                )
              })}
            </Grid>
          )}

          {!loadingHistory && history.length === 0 && (
            <Text color="gray.500" textAlign="center" py={10}>
              Nenhum registro encontrado.
            </Text>
          )}
        </Box>

        <Button variant="outline" onClick={() => navigate("/home")}>
          Voltar para Home
        </Button>
      </Stack>

      <AnalysisDetailDialog
        item={selectedItem}
        open={detailOpen}
        onClose={() => {
          setDetailOpen(false)
          setSelectedItem(null)
        }}
      />
    </Container>
  )
}