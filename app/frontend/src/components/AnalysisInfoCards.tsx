import { Box, Flex, Text } from "@chakra-ui/react"
import { Activity, Info, Microscope } from "lucide-react"
import type { ReactNode } from "react"

import { COLORS } from "../constants/colors"
import { formatAnalysisDate, formatConfidence } from "../utils/formatAnalysis"
import type { HistoryItem } from "../types/analysis"

function CardIcon({ children }: { children: ReactNode }) {
  return (
    <Flex
      align="center"
      justify="center"
      w="36px"
      h="36px"
      minW="36px"
      borderRadius="full"
      bg={COLORS.purple}
      color="white"
    >
      {children}
    </Flex>
  )
}

function InfoCard({
  icon,
  title,
  highlight = false,
  children,
}: {
  icon: ReactNode
  title: string
  highlight?: boolean
  children: ReactNode
}) {
  return (
    <Box
      bg={highlight ? COLORS.surface : "#F5F5F5"}
      borderRadius="12px"
      p={4}
    >
      <Flex align="center" gap={3} mb={3}>
        <CardIcon>{icon}</CardIcon>
        <Text color={COLORS.blueText} fontWeight="bold" fontSize="sm">
          {title}
        </Text>
      </Flex>
      {children}
    </Box>
  )
}

type AnalysisInfoCardsProps = {
  prediction: string
  confidence?: number
  createdAt?: string
  allowForTraining?: boolean
  recordId?: string
}

export default function AnalysisInfoCards({
  prediction,
  confidence,
  createdAt,
  allowForTraining,
  recordId,
}: AnalysisInfoCardsProps) {
  return (
    <Flex direction="column" gap={3}>
      <InfoCard icon={<Microscope size={18} />} title="Detalhes da Análise" highlight>
        <Text color={COLORS.blueText} fontSize="sm">
          <Text as="span" fontWeight="bold">
            Predição:{" "}
          </Text>
          {prediction}
        </Text>
        <Text color={COLORS.blueText} fontSize="sm" mt={1}>
          <Text as="span" fontWeight="bold">
            Confiança:{" "}
          </Text>
          {formatConfidence(confidence)}%
        </Text>
      </InfoCard>

      <InfoCard icon={<Info size={18} />} title="Informações">
        <Text color={COLORS.blueText} fontSize="sm">
          <Text as="span" fontWeight="bold">
            Data da Análise:{" "}
          </Text>
          {formatAnalysisDate(createdAt)}
        </Text>
        <Text color={COLORS.blueText} fontSize="sm" mt={1}>
          <Text as="span" fontWeight="bold">
            Uso para Treinamento:{" "}
          </Text>
          {allowForTraining ? "Autorizado" : "Não Autorizado"}
        </Text>
        {recordId && (
          <Text color={COLORS.blueText} fontSize="sm" mt={1} wordBreak="break-all">
            <Text as="span" fontWeight="bold">
              ID do Registro:{" "}
            </Text>
            {recordId}
          </Text>
        )}
      </InfoCard>

      <InfoCard icon={<Activity size={18} />} title="Visão do Profissional de Saúde">
        <Text color={COLORS.blueText} fontSize="sm" lineHeight="tall">
          O mapa de calor destaca as regiões da imagem que mais influenciaram a
          decisão do modelo de inteligência artificial.
        </Text>
      </InfoCard>
    </Flex>
  )
}

export function analysisItemToCardsProps(item: HistoryItem): AnalysisInfoCardsProps {
  return {
    prediction: item.prediction ?? "—",
    confidence: item.confidence,
    createdAt: item.createdAt,
    allowForTraining: item.allowForTraining,
    recordId: item.id,
  }
}
