import {
  Badge,
  Box,
  Button,
  Container,
  Heading,
  Stack,
  Text,
} from "@chakra-ui/react"
import { useEffect } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import AnalysisImagePair from "../../components/AnalysisImagePair"
import type { AnalyzeResult } from "../../types/analysis"

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
            A imagem abaixo mostra as regiões que mais influenciaram a decisão do modelo.
          </Text>
        </Box>

        {focusState.result && (
          <Box p={4} borderRadius="md" bg={focusState.result.detected ? "red.500" : "green.500"} color="white">
            <Text fontWeight="bold">
              Predição: {focusState.result.detected ? "Hanseníase" : "Não Detectado"}
            </Text>
            <Text>Confiança: {focusState.result.probability}%</Text>
          </Box>
        )}

        <AnalysisImagePair
          originalSrc={focusState.preview}
          focusSrc={focusState.focusPreview}
        />

        <Badge colorScheme="teal" w="fit-content">
          Grad-CAM — explicação visual da predição
        </Badge>

        <Stack direction={{ base: "column", md: "row" }} gap={4}>
          <Button colorScheme="teal" onClick={() => navigate("/home")}>
            Nova Análise
          </Button>
          <Button variant="outline" onClick={() => navigate("/analyze")}>
            Voltar
          </Button>
        </Stack>
      </Stack>
    </Container>
  )
}
