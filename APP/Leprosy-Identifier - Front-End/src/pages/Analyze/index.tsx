import {
  Box,
  Button,
  Container,
  Heading,
  Image,
  Stack,
  Text,
  Spinner,
} from "@chakra-ui/react"
import { useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { useAuth } from "../../contexts/AuthContext"

type ResultType = {
  detected: boolean
  probability: number
}

export default function Analyze() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const { user } = useAuth()

  const image = state?.preview as string | undefined
  const file = state?.file as File | undefined

  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ResultType | null>(null)

  async function handleAnalyze() {
    if (!file || !user) return

    try {
      setLoading(true)

      const formData = new FormData()
      formData.append("image", file)

      const predResponse = await fetch(
        `${import.meta.env.VITE_API_URL}/prediction_data/`,
        {
          method: "POST",
          body: formData,
        }
      )

      if (!predResponse.ok) throw new Error("Erro na predição")
      const predData = await predResponse.json()

      const isHanseniase = predData.predicted_class !== "outro"
      const probabilityPercent = Number((predData.probability * 100).toFixed(2))

      setResult({
        detected: isHanseniase,
        probability: probabilityPercent,
      })

      const convResponse = await fetch(
        `${import.meta.env.VITE_API_URL}/image/convert/`,
        {
          method: "POST",
          body: formData,
        }
      )

      if (!convResponse.ok) throw new Error("Erro na conversão")
      const convData = await convResponse.json()

      await fetch(
        `${import.meta.env.VITE_API_URL}/predictions/save/`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_id: user.uid,
            image_base64: convData.base64,
            prediction: isHanseniase ? "Hanseníase" : "Outro",
            confidence: predData.probability,
            model_version: "v1.0"
          }),
        }
      )

    } catch (error) {
      console.error(error)
      alert("Ocorreu um erro durante o processamento.")
    } finally {
      setLoading(false)
    }
  }

  if (!image) {
    return (
      <Container py={10}>
        <Button onClick={() => navigate("/home")}>Voltar</Button>
      </Container>
    )
  }

  return (
    <Container py={8}>
      <Stack gap={6}>
        <Heading size="lg">Análise da imagem</Heading>

        <Image src={image} borderRadius="xl" objectFit="cover" maxH="320px" />

        <Button
          colorScheme="teal"
          size="lg"
          onClick={handleAnalyze}
          loading={loading}
          disabled={loading || !!result}
        >
          {loading ? <Spinner size="sm" /> : "Analisar"}
        </Button>

        {result && (
          <Box
            p={6}
            borderRadius="xl"
            bg={result.detected ? "red.500" : "green.500"}
            color="white"
            textAlign="center"
          >
            <Text fontSize="lg" fontWeight="bold">
              Hanseníase detectada: {result.detected ? "Sim" : "Não"}
            </Text>
            <Text mt={2}>Probabilidade: {result.probability}%</Text>
          </Box>
        )}

        <Button variant="ghost" onClick={() => navigate("/home")}>
          Voltar para Início
        </Button>
      </Stack>
    </Container>
  )
}