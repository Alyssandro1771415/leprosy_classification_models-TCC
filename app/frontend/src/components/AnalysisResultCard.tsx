import { Box, Flex, Text } from "@chakra-ui/react"
import { Microscope } from "lucide-react"

import { COLORS } from "../constants/colors"
import { formatConfidence } from "../utils/formatAnalysis"

type AnalysisResultCardProps = {
  prediction: string
  confidence?: number
}

export default function AnalysisResultCard({
  prediction,
  confidence,
}: AnalysisResultCardProps) {
  return (
    <Box bg={COLORS.surface} borderRadius="14px" p={4}>
      <Flex align="center" gap={3} mb={3}>
        <Flex
          align="center"
          justify="center"
          w="40px"
          h="40px"
          minW="40px"
          borderRadius="full"
          bg={COLORS.purple}
          color="white"
          flexShrink={0}
        >
          <Microscope size={20} />
        </Flex>
        <Text color={COLORS.blueText} fontWeight="bold" fontSize="15px">
          Detalhes da Análise
        </Text>
      </Flex>

      <Text color={COLORS.blueText} fontSize="14px" lineHeight="1.5">
        <Text as="span" fontWeight="bold">
          Predição:{" "}
        </Text>
        {prediction}
      </Text>
      <Text color={COLORS.blueText} fontSize="14px" lineHeight="1.5" mt={1}>
        <Text as="span" fontWeight="bold">
          Confiança:{" "}
        </Text>
        {formatConfidence(confidence)}%
      </Text>
    </Box>
  )
}
