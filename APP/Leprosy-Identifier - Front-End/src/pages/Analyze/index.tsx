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

export default function Analyze() {
  const { state } = useLocation()
  const navigate = useNavigate()

  const image = state?.preview as string | undefined
  const file = state?.file as File | undefined

  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<string | null>(null)

  function handleAnalyze() {
    if (!file) return

    setLoading(true)

    setTimeout(() => {
      setResult("Hanseníase detectada (exemplo)")
      setLoading(false)
    }, 2000)
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

  const isPositive = result?.toLowerCase().includes("detectada")

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
            bg={isPositive ? "red.500" : "green.500"}
            color="white"
            textAlign="center"
          >
            <Text fontSize="lg" fontWeight="bold">
              {result}
            </Text>
          </Box>
        )}
      </Stack>
    </Container>
  )
}