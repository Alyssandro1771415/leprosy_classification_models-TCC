import {
  Box,
  Button,
  Flex,
  IconButton,
  Input,
  Spinner,
  Text,
} from "@chakra-ui/react"
import { Microscope, Search } from "lucide-react"
import { useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import { FiMenu } from "react-icons/fi"

import { FIXED_BOTTOM_OFFSET } from "../../constants/layout"
import HistoryListItem from "../../components/HistoryListItem"
import { COLORS } from "../../constants/colors"
import { useAuth } from "../../contexts/AuthContext"
import { useDrawer } from "../../contexts/DrawerContext"
import { useAnalysisHistory } from "../../hooks/useAnalysisHistory"
import { deleteAnalysis } from "../../services/analysisService"
import type { HistoryItem } from "../../types/analysis"
import { formatAnalysisDate, formatConfidence } from "../../utils/formatAnalysis"

function filterHistory(items: HistoryItem[], query: string): HistoryItem[] {
  const normalized = query.trim().toLowerCase()
  if (!normalized) return items

  return items.filter((item) => {
    const title = (item.prediction ?? "Análise").toLowerCase()
    const date = formatAnalysisDate(item.createdAt).toLowerCase()
    const confidence = formatConfidence(item.confidence)

    return (
      title.includes(normalized) ||
      date.includes(normalized) ||
      confidence.includes(normalized)
    )
  })
}

export default function Home() {
  const navigate = useNavigate()
  const { openDrawer } = useDrawer()
  const { user } = useAuth()
  const { history, loading, error, refetch } = useAnalysisHistory()

  const [search, setSearch] = useState("")

  const filteredHistory = useMemo(
    () => filterHistory(history, search),
    [history, search],
  )

  function openDetails(item: HistoryItem) {
    const id = item.id ?? "unknown"
    navigate(`/analysis/${id}`, { state: { item } })
  }

  async function handleDelete(item: HistoryItem) {
    if (!user?.uid || !item.id) {
      alert("Não foi possível identificar a análise para exclusão")
      return
    }

    const confirmed = window.confirm(
      "Deseja excluir esta análise? Esta ação não pode ser desfeita.",
    )

    if (!confirmed) return

    try {
      await deleteAnalysis(user.uid, item.id)
      await refetch()
    } catch (error) {
      console.error(error)
      alert("Erro ao excluir análise")
    }
  }

  return (
    <Flex direction="column" minH="100dvh" bg="white" align="center">
      <Box w="100%" maxW="430px" flex="1" display="flex" flexDirection="column">
        <Flex
          align="center"
          justify="center"
          position="relative"
          px="16px"
          pt="10px"
          pb="6px"
          minH="52px"
        >
          <IconButton
            aria-label="Abrir menu"
            variant="ghost"
            position="absolute"
            left="8px"
            size="md"
            color={COLORS.purple}
            onClick={openDrawer}
            _hover={{ bg: "gray.100" }}
          >
            <FiMenu size={24} strokeWidth={2.5} />
          </IconButton>

          <Text
            color={COLORS.blueText}
            fontWeight="bold"
            fontSize="17px"
            lineHeight="1.2"
          >
            Histórico de Análise
          </Text>
        </Flex>

        <Box px="16px" pb="12px">
          <Flex
            align="center"
            bg="#EBEBEB"
            borderRadius="999px"
            px="16px"
            h="46px"
            gap="10px"
          >
            <Search size={20} color={COLORS.purple} strokeWidth={2.5} />
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              border="none"
              bg="transparent"
              color={COLORS.blueText}
              fontSize="15px"
              h="100%"
              p={0}
              _placeholder={{ color: "transparent" }}
              _focus={{ outline: "none", boxShadow: "none" }}
            />
          </Flex>
        </Box>

        <Box flex="1" overflowY="auto" pb={`calc(120px + ${FIXED_BOTTOM_OFFSET})`}>
          {loading ? (
            <Flex justify="center" py={20}>
              <Spinner size="lg" color={COLORS.purple} />
            </Flex>
          ) : error ? (
            <Text textAlign="center" color="red.400" py={20} px={6} fontSize="15px">
              {error}
              {" "}Verifique se o backend está rodando e o cabo USB conectado.
            </Text>
          ) : filteredHistory.length > 0 ? (
            <Box>
              {filteredHistory.map((item, index) => (
                <HistoryListItem
                  key={`${item.id ?? "analysis"}-${index}`}
                  item={item}
                  showDivider={index < filteredHistory.length - 1}
                  onClick={() => openDetails(item)}
                  onDelete={() => handleDelete(item)}
                />
              ))}
            </Box>
          ) : (
            <Text textAlign="center" color="gray.400" py={20} px={6} fontSize="15px">
              {search
                ? "Nenhuma análise encontrada para esta busca."
                : "Nenhuma análise registrada ainda."}
            </Text>
          )}
        </Box>

        <Box
          position="fixed"
          bottom={0}
          left="50%"
          transform="translateX(-50%)"
          w="100%"
          maxW="430px"
          px="16px"
          pb={FIXED_BOTTOM_OFFSET}
          pt="10px"
          bg="white"
        >
          <Button
            w="100%"
            h="54px"
            bg={COLORS.purple}
            color="white"
            borderRadius="14px"
            fontWeight="bold"
            fontSize="15px"
            letterSpacing="0.06em"
            textTransform="uppercase"
            onClick={() => navigate("/analyze/new")}
            _hover={{ bg: "#351049" }}
          >
            <Flex align="center" justify="center" gap="10px">
              <Microscope size={20} strokeWidth={2.5} />
              Nova Análise
            </Flex>
          </Button>
        </Box>
      </Box>
    </Flex>
  )
}
