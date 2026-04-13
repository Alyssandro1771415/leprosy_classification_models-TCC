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
import { useAuth } from "../../contexts/AuthContext"

export default function Analyze() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const { user } = useAuth()

  const image = state?.preview as string | undefined
  const file = state?.file as File | undefined

  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [history, setHistory] = useState<any[]>([])
  const [loadingHistory, setLoadingHistory] = useState(false)

  // Estado para o consentimento
  const [allowForTraining, setAllowForTraining] = useState("false")

  const fetchHistory = useCallback(async () => {
    if (!user?.uid) return

    try {
      setLoadingHistory(true)
      console.log(`${import.meta.env.VITE_API_LINK}/predictions/history/${user.uid}`)
      const response = await fetch(
        `${import.meta.env.VITE_API_LINK}/predictions/history/${user.uid}`, {
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
      const formData = new FormData()
      formData.append("image", file)

      const predRes = await fetch(`${import.meta.env.VITE_API_LINK}/prediction_data`, {
        method: "POST",
        headers: {
          "x-access-token": import.meta.env.VITE_SECRET_TOKEN
        },
        body: formData,
      })
      const predData = await predRes.json()
      const isHanseniase = predData.predicted_class !== "outro"

      const convRes = await fetch(`${import.meta.env.VITE_API_LINK}/image/convert`, {
        method: "POST",
        headers: {
          "x-access-token": import.meta.env.VITE_SECRET_TOKEN
        },
        body: formData,
      })
      const convData = await convRes.json()

      const saveRes = await fetch(`${import.meta.env.VITE_API_LINK}/predictions/save`, {
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
          model_version: "v1.0",
          allow_for_training: allowForTraining === "true"
        }),
      })

      if (saveRes.ok) {
        setResult({
          detected: isHanseniase,
          probability: (predData.probability * 100).toFixed(2)
        })
        fetchHistory()
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
                const rawString = item.imageBase64 || "";
                const cleanBase64 = rawString.replace(/\s/g, '');

                const imageSrc = cleanBase64
                  ? `data:image/png;base64,${cleanBase64}`
                  : "https://via.placeholder.com/150";

                return (
                  <Box key={index} p={3} borderRadius="lg" border="1px solid" borderColor="gray.200">
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
    </Container>
  )
}