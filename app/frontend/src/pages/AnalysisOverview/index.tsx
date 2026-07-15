import { Box, Flex, IconButton } from "@chakra-ui/react"
import { Microscope, Trash2 } from "lucide-react"
import { useEffect, useMemo, useState } from "react"
import { useLocation, useNavigate, useParams } from "react-router-dom"

import { FIXED_BOTTOM_OFFSET } from "../../constants/layout"
import AnalysisInfoCards, {
  analysisItemToCardsProps,
} from "../../components/AnalysisInfoCards"
import { PrimaryActionButton } from "../../components/ActionButtons"
import ImageCarousel from "../../components/ImageCarousel"
import { PageHeader } from "../../components/PageHeader"
import { COLORS } from "../../constants/colors"
import { useAuth } from "../../contexts/AuthContext"
import { useAnalysisHistory } from "../../hooks/useAnalysisHistory"
import { deleteAnalysis, fetchFocusMaps } from "../../services/analysisService"
import type { HistoryItem } from "../../types/analysis"
import { base64ToDataUrl, base64ToFile } from "../../utils/imageUtils"

export default function AnalysisOverview() {
  const navigate = useNavigate()
  const { id } = useParams()
  const { state } = useLocation()
  const { user } = useAuth()
  const { history, refetch } = useAnalysisHistory()

  const itemFromState = (state as { item?: HistoryItem } | null)?.item
  const item = useMemo(
    () => itemFromState ?? history.find((entry) => entry.id === id),
    [itemFromState, history, id],
  )

  const [preprocessedPreview, setPreprocessedPreview] = useState<string | null>(null)
  const [focusPreview, setFocusPreview] = useState<string | null>(null)
  const [loadingFocus, setLoadingFocus] = useState(false)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    if (!item?.imageBase64) return

    let cancelled = false

    async function loadFocus() {
      try {
        setLoadingFocus(true)
        const file = base64ToFile(item!.imageBase64!, `analysis-${item!.id ?? "detail"}.png`)
        const focus = await fetchFocusMaps(file)

        if (!cancelled) {
          setFocusPreview(focus.focusPreview)
          setPreprocessedPreview(focus.preprocessedPreview ?? null)
        }
      } catch (error) {
        console.error("Erro ao buscar mapa de calor:", error)
      } finally {
        if (!cancelled) setLoadingFocus(false)
      }
    }

    loadFocus()
    return () => {
      cancelled = true
    }
  }, [item])

  async function handleDelete() {
    if (!user?.uid || !item?.id) return

    const confirmed = window.confirm(
      "Deseja excluir esta análise? Esta ação não pode ser desfeita.",
    )

    if (!confirmed) return

    try {
      setDeleting(true)
      await deleteAnalysis(user.uid, item.id)
      await refetch()
      navigate("/home", { replace: true })
    } catch (error) {
      console.error(error)
      alert("Erro ao excluir análise")
    } finally {
      setDeleting(false)
    }
  }

  if (!item) {
    return (
      <Flex direction="column" minH="100dvh" bg={COLORS.pageBg}>
        <PageHeader title="Visão Geral" backTo="/home" />
      </Flex>
    )
  }

  const originalSrc = item.imageBase64 ? base64ToDataUrl(item.imageBase64) : ""

  const slides = [
    { src: originalSrc, label: "Imagem Original" },
    ...(preprocessedPreview
      ? [{ src: preprocessedPreview, label: "Pré-processamento (Canal Y + Bilateral)" }]
      : []),
    ...(focusPreview
      ? [{ src: focusPreview, label: "Mapa de Calor (Grad-CAM)" }]
      : []),
  ]

  return (
    <Flex direction="column" minH="100dvh" bg={COLORS.pageBg}>
      <PageHeader
        title="Visão Geral"
        backTo="/home"
        rightAction={
          <IconButton
            aria-label="Excluir análise"
            variant="ghost"
            size="md"
            minW="44px"
            h="44px"
            color={COLORS.purple}
            onClick={handleDelete}
            disabled={deleting}
            _hover={{ bg: "gray.100" }}
          >
            <Trash2 size={28} strokeWidth={2.5} />
          </IconButton>
        }
      />

      <Box flex="1" overflowY="auto" px={6} pb={`calc(130px + ${FIXED_BOTTOM_OFFSET})`}>
        <ImageCarousel slides={slides} loading={loadingFocus && slides.length <= 1} />
        <Box mt={6}>
          <AnalysisInfoCards {...analysisItemToCardsProps(item)} />
        </Box>
      </Box>

      <Box
        position="fixed"
        bottom={0}
        left={0}
        right={0}
        px={6}
        pb={FIXED_BOTTOM_OFFSET}
        pt={3}
        bg="white"
      >
        <PrimaryActionButton onClick={() => navigate("/analyze/new")}>
          <Flex align="center" justify="center" gap={2}>
            <Microscope size={18} />
            Nova Análise
          </Flex>
        </PrimaryActionButton>
      </Box>
    </Flex>
  )
}
