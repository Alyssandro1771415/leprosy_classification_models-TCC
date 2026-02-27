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

type ResultType = {
  detected: boolean
  probability: number
}

export default function Analyze() {
  const { state } = useLocation()
  const navigate = useNavigate()

  const image = state?.preview as string | undefined
  const file = state?.file as File | undefined

  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ResultType | null>(null)

  async function handleAnalyze() {
    if (!file) return

    try {
      setLoading(true)

      const formData = new FormData()
      formData.append("image", file)

      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/prediction_data`,
        {
          method: "POST",
          body: formData,
        }
      )

      if (!response.ok) {
        throw new Error("Erro na requisição")
      }

      const data = await response.json()

      const isHanseniase = data.predicted_class !== "outro"
      const probabilityPercent = Number(
        (data.probability * 100).toFixed(2)
      )

      setResult({
        detected: isHanseniase,
        probability: probabilityPercent,
      })
    } catch (error) {
      console.error(error)
      setResult(null)
      alert("Erro ao analisar imagem")
    } finally {
      setLoading(false)
    }
  }

  if (!image) {
    return (
      <Container py={10}>
        <Stack gap={6} textAlign="center">
          <Heading size="md">Nenhuma imagem enviada</Heading>

          <Button colorScheme="teal" onClick={() => navigate("/home")}>
            Voltar
          </Button>
        </Stack>
      </Container>
    )
  }

  return (
    <Container py={8}>
      <Stack gap={6}>
        <Heading size="lg">Análise da imagem</Heading>

        <Image
          src={image}
          borderRadius="xl"
          objectFit="cover"
          maxH="320px"
        />

        <Button
          colorScheme="teal"
          size="lg"
          onClick={handleAnalyze}
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

            <Text mt={2}>
              Probabilidade: {result.probability}%
            </Text>
          </Box>
        )}
      </Stack>
    </Container>
  )
}