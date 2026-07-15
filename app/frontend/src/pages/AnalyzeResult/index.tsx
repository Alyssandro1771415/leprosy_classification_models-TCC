import { Box, Flex, Stack, Text } from "@chakra-ui/react"
import { useEffect, useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"

import AnalysisResultCard from "../../components/AnalysisResultCard"
import {
  OutlineActionButton,
  PrimaryActionButton,
} from "../../components/ActionButtons"
import ImageCarousel from "../../components/ImageCarousel"
import { PageHeader } from "../../components/PageHeader"
import { COLORS } from "../../constants/colors"
import { FIXED_BOTTOM_OFFSET } from "../../constants/layout"
import { useAuth } from "../../contexts/AuthContext"
import { saveAnalysis } from "../../services/analysisService"
import type { ResultFlowState } from "../../types/flow"

export default function AnalyzeResult() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { state } = useLocation()
  const flowState = state as ResultFlowState | null
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!flowState?.preview || !flowState?.focusPreview || !flowState?.result) {
      navigate("/analyze/new", { replace: true })
    }
  }, [flowState, navigate])

  if (!flowState?.preview || !flowState?.focusPreview || !flowState?.result) {
    return null
  }

  const slides = [
    { src: flowState.preview, label: "Imagem Original" },
    ...(flowState.preprocessedPreview
      ? [{ src: flowState.preprocessedPreview, label: "Pré-processamento (Canal Y + Bilateral)" }]
      : []),
    { src: flowState.focusPreview, label: "Mapa de Calor (Grad-CAM)" },
  ]

  async function handleSave() {
    if (!user) return

    try {
      setSaving(true)
      await saveAnalysis({
        user,
        imageBase64: flowState!.imageBase64,
        prediction: flowState!.result.prediction,
        confidence: flowState!.result.probability,
        allowForTraining: flowState!.allowForTraining,
      })
      navigate("/home", { replace: true })
    } catch (error) {
      console.error(error)
      const message =
        error instanceof Error ? error.message : "Erro ao salvar análise"
      alert(message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Flex
      direction="column"
      minH="100dvh"
      bg={COLORS.pageBg}
      align="center"
      color={COLORS.blueText}
    >
      <Box w="100%" maxW="430px" flex="1" display="flex" flexDirection="column">
        <PageHeader title="Nova Análise" backTo="/analyze/consent" />

        <Box flex="1" overflowY="auto" px="16px" pb="8px">
          <ImageCarousel slides={slides} imageFit="cover" />

          <Box mt={6} mb={4} textAlign="center">
            <Text fontWeight="bold" fontSize="15px" color={COLORS.blueText} mb={2}>
              Foco do Modelo
            </Text>
            <Text fontSize="14px" lineHeight="tall" color={COLORS.blueText} px={2}>
              Visualização da imagem original, do pré-<br></br>processamento (canal Y +
              bilateral) e das regiões que<br></br> mais influenciaram a decisão do modelo.
            </Text>
          </Box>

          <AnalysisResultCard
            prediction={flowState.result.prediction}
            confidence={flowState.result.probability}
          />
        </Box>

        <Stack px="16px" pb={FIXED_BOTTOM_OFFSET} pt="8px" gap={3} bg={COLORS.pageBg}>
          <PrimaryActionButton onClick={handleSave} loading={saving}>
            Salvar Análise
          </PrimaryActionButton>
          <OutlineActionButton onClick={() => navigate("/home")}>
            Cancelar
          </OutlineActionButton>
        </Stack>
      </Box>
    </Flex>
  )
}
