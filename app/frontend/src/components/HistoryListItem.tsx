import { Box, Flex, IconButton, Image, Menu, Portal, Text } from "@chakra-ui/react"
import { FiMoreVertical } from "react-icons/fi"

import { COLORS } from "../constants/colors"
import type { HistoryItem } from "../types/analysis"
import { formatAnalysisDate, formatConfidence } from "../utils/formatAnalysis"
import { base64ToDataUrl } from "../utils/imageUtils"

function AnalysisListIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M9 3h6v2.2l1.8 7.2c.5 2-.2 4.1-1.8 5.5-1.6 1.4-3.8 1.9-5.8 1.3-2-.6-3.5-2.2-4-4.2L5 5.2V3h4z"
        stroke="white"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <circle cx="15.5" cy="15.5" r="4.5" stroke="white" strokeWidth="1.6" />
      <path d="M18.5 18.5L21 21" stroke="white" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  )
}

type HistoryListItemProps = {
  item: HistoryItem
  onClick: () => void
  onDelete?: () => void
  showDivider?: boolean
}

export default function HistoryListItem({
  item,
  onClick,
  onDelete,
  showDivider = true,
}: HistoryListItemProps) {
  const imageSrc = item.imageBase64
    ? base64ToDataUrl(item.imageBase64)
    : undefined

  const title = item.prediction ?? "Título da Análise"

  return (
    <Flex
      align="flex-start"
      w="100%"
      px="16px"
      py="14px"
      gap="12px"
      cursor="pointer"
      onClick={onClick}
      borderBottom={showDivider ? "1px solid #E5E5E5" : "none"}
      _hover={{ bg: "gray.50" }}
      _active={{ bg: "gray.100" }}
    >
      {/* Esquerda: ícone + textos agrupados (sem flex-grow) */}
      <Flex align="center" gap="10px" flexShrink={0} minW={0}>
        <Flex
          align="center"
          justify="center"
          w="44px"
          h="44px"
          minW="44px"
          borderRadius="full"
          bg={COLORS.purple}
          flexShrink={0}
        >
          <AnalysisListIcon />
        </Flex>

        <Box minW={0} w="108px">
          <Text
            color={COLORS.purple}
            fontWeight="bold"
            fontSize="15px"
            lineHeight="1.2"
            mb="6px"
            truncate
          >
            {title}
          </Text>
          <Text
            color={COLORS.blueText}
            fontSize="13px"
            lineHeight="1.25"
            mb="4px"
          >
            Confiança:{" "}
            <Text as="span" fontWeight="bold">
              {formatConfidence(item.confidence)}%
            </Text>
          </Text>
          <Text color={COLORS.blueText} fontSize="12px" lineHeight="1.25">
            {formatAnalysisDate(item.createdAt)}
          </Text>
        </Box>
      </Flex>

      {/* Direita: thumbnail + menu */}
      <Flex align="flex-start" gap="6px" ml="auto" flexShrink={0}>
        <Box w="150px" h="57px" flexShrink={0}>
          {imageSrc ? (
            <Image
              src={imageSrc}
              alt={title}
              w="100%"
              h="100%"
              borderRadius="12px"
              objectFit="cover"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = "none"
              }}
            />
          ) : (
            <Box w="100%" h="100%" borderRadius="12px" bg="#EBEBEB" />
          )}
        </Box>

        <Menu.Root>
          <Menu.Trigger asChild>
            <IconButton
              aria-label="Opções da análise"
              variant="ghost"
              size="sm"
              minW="24px"
              w="24px"
              h="24px"
              mt="2px"
              p={0}
              color={COLORS.purple}
              flexShrink={0}
              onClick={(e) => e.stopPropagation()}
              _hover={{ bg: "transparent", opacity: 0.7 }}
            >
              <FiMoreVertical size={18} strokeWidth={2.5} />
            </IconButton>
          </Menu.Trigger>
          <Portal>
            <Menu.Positioner>
              <Menu.Content minW="140px" py={1}>
                <Menu.Item
                  value="delete"
                  color={COLORS.purple}
                  fontWeight="medium"
                  fontSize="sm"
                  onClick={(e) => {
                    e.stopPropagation()
                    onDelete?.()
                  }}
                >
                  Excluir
                </Menu.Item>
              </Menu.Content>
            </Menu.Positioner>
          </Portal>
        </Menu.Root>
      </Flex>
    </Flex>
  )
}
