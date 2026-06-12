import {
  Badge,
  Box,
  Button,
  Container,
  Grid,
  Heading,
  Image,
  Stack,
  Text,
} from "@chakra-ui/react"
import { useEffect } from "react"
import { useLocation, useNavigate } from "react-router-dom"

type AnalyzeResult = {
  detected: boolean
  probability: string
}

type FocusState = {
  preview?: string
  focusPreview?: string
  result?: AnalyzeResult
}

export default function ModelFocus() {
  const navigate = useNavigate()
  const { state } = useLocation()
  const focusState = (state as FocusState | null) ?? null

  useEffect(() => {
    if (!focusState?.preview || !focusState?.focusPreview) {
      navigate("/home", { replace: true })
    }
  }, [focusState, navigate])

  if (!focusState?.preview || !focusState?.focusPreview) {
    return null
  }

  return (
    <Container py={8} maxW="5xl">
      <Stack gap={8}>
        <Box>
          <Heading size="lg" mb={2}>Foco do Modelo</Heading>
          <Text color="gray.500">
            A imagem abaixo mostra as regioes que mais influenciaram a decisao do modelo.
          </Text>
        </Box>

        {focusState.result && (
          <Box p={4} borderRadius="md" bg={focusState.result.detected ? "red.500" : "green.500"} color="white">
            <Text fontWeight="bold">
              Predicao: {focusState.result.detected ? "Hanseniase" : "Nao Detectado"}
            </Text>
            <Text>Confianca: {focusState.result.probability}%</Text>
          </Box>
        )}

        <Grid templateColumns={{ base: "1fr", md: "1fr 1fr" }} gap={6}>
          <Box>
            <Heading size="sm" mb={3}>Imagem Original</Heading>
            <Image
              src={focusState.preview}
              alt="Imagem original enviada para classificacao"
              borderRadius="lg"
              objectFit="cover"
              w="100%"
              maxH="420px"
            />
          </Box>

          <Box>
            <Heading size="sm" mb={3}>Mapa de Foco do Modelo</Heading>
            <Image
              src={focusState.focusPreview}
              alt="Imagem com foco destacado pelo modelo"
              borderRadius="lg"
              objectFit="cover"
              w="100%"
              maxH="420px"
            />
            <Badge mt={3} colorScheme="teal">
              Grad-CAM
            </Badge>
          </Box>
        </Grid>

        <Stack direction={{ base: "column", md: "row" }} gap={4}>
          <Button colorScheme="teal" onClick={() => navigate("/home")}>
            Nova Analise
          </Button>
          <Button variant="outline" onClick={() => navigate("/analyze")}>
            Voltar
          </Button>
        </Stack>
      </Stack>
    </Container>
  )
}
