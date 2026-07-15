import {
  Box,
  Flex,
  Image,
  Stack,
  Text,
} from "@chakra-ui/react"
import { useEffect, useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"

import {
  OutlineActionButton,
  PrimaryActionButton,
} from "../../components/ActionButtons"
import { PageHeader } from "../../components/PageHeader"
import { COLORS } from "../../constants/colors"
import { FIXED_BOTTOM_OFFSET } from "../../constants/layout"
import {
  convertImageToBase64,
  fetchFocusMaps,
  runPrediction,
} from "../../services/analysisService"
import type { ConsentFlowState } from "../../types/flow"

export default function AnalyzeConsent() {
  const navigate = useNavigate()
  const { state } = useLocation()
  const flowState = state as ConsentFlowState | null

  const [allowForTraining, setAllowForTraining] = useState("false")
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!flowState?.file || !flowState?.preview) {
      navigate("/analyze/new", { replace: true })
    }
  }, [flowState, navigate])

  if (!flowState?.file || !flowState?.preview) return null

  async function handleDiagnose() {
    try {
      setLoading(true)

      const [result, focus, imageBase64] = await Promise.all([
        runPrediction(flowState!.file),
        fetchFocusMaps(flowState!.file),
        convertImageToBase64(flowState!.file),
      ])

      navigate("/analyze/result", {
        state: {
          file: flowState!.file,
          preview: flowState!.preview,
          allowForTraining: allowForTraining === "true",
          result: {
            detected: result.detected,
            prediction: result.prediction,
            probability: result.probability,
            probabilityDisplay: result.probabilityDisplay,
          },
          preprocessedPreview: focus.preprocessedPreview,
          focusPreview: focus.focusPreview,
          imageBase64,
        },
      })
    } catch (error) {
      console.error(error)
      alert("Erro no processamento")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Flex direction="column" minH="100dvh" bg="white">
      <PageHeader title="Nova Análise" backTo="/analyze/new" />

      <Stack flex="1" px={6} py={4} gap={6} pb={2}>
        <Flex justify="center">
          <Image
            src={flowState.preview}
            alt="Imagem selecionada"
            w="400px"
            h="460px"
            maxW="100%"
            objectFit="cover"
            borderRadius="16px"
          />
        </Flex>

        <Box textAlign="center">
          <Text
            color={COLORS.blueText}
            fontWeight="bold"
            fontSize="sm"
            letterSpacing="wider"
            textTransform="uppercase"
            mb={3}
          >
            Atenção
          </Text>
          <Text
            color={COLORS.blueText}
            w="300px"
            h="42px"
            mx="auto"
            fontSize="xs"
            lineHeight="1.3"
            textAlign="center"
          >
            Permito o uso da seguinte imagem para uso posterior de treinamento e
            aprimoramento da Inteligência Artificial responsável pelo diagnóstico
            neste app.
          </Text>
        </Box>

        <Flex justify="center" gap={8}>
          {(["true", "false"] as const).map((value) => (
            <Box
              as="label"
              key={value}
              display="flex"
              alignItems="center"
              gap={2}
              cursor="pointer"
            >
              <input
                type="radio"
                name="allowForTraining"
                value={value}
                checked={allowForTraining === value}
                onChange={(e) => setAllowForTraining(e.target.value)}
                style={{
                  width: "18px",
                  height: "18px",
                  accentColor: COLORS.purple,
                  cursor: "pointer",
                }}
              />
              <Text color={COLORS.purple} fontWeight="bold" fontSize="sm">
                {value === "true" ? "Sim" : "Não"}
              </Text>
            </Box>
          ))}
        </Flex>
      </Stack>

      <Stack px={6} pb={FIXED_BOTTOM_OFFSET} gap={3}>
        <PrimaryActionButton onClick={handleDiagnose} loading={loading}>
          Realizar Diagnóstico
        </PrimaryActionButton>
        <OutlineActionButton onClick={() => navigate("/home")}>
          Cancelar
        </OutlineActionButton>
      </Stack>
    </Flex>
  )
}
