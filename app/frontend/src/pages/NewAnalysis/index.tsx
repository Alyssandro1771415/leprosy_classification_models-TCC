import { Box, Flex, Stack, Text } from "@chakra-ui/react"
import { Camera, ImageIcon } from "lucide-react"
import { useRef } from "react"
import { useNavigate } from "react-router-dom"

import DashedActionButton from "../../components/ActionButtons"
import { PageHeader } from "../../components/PageHeader"
import { COLORS } from "../../constants/colors"
import { FIXED_BOTTOM_OFFSET } from "../../constants/layout"
import illustrationImg from "../../imagens_APP_TCC/75d27ff569613c77972f0ecb78dc5dd115def8d6.png"

export default function NewAnalysis() {
  const navigate = useNavigate()
  const cameraInputRef = useRef<HTMLInputElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  function handleFileChange(file: File | undefined) {
    if (!file) return

    navigate("/analyze/consent", {
      state: {
        file,
        preview: URL.createObjectURL(file),
      },
    })
  }

  return (
    <Flex direction="column" minH="100dvh" bg="white">
      <PageHeader title="Nova Análise" backTo="/home" />

      <Stack flex="1" px={6} py={6} gap={8} align="center" pb={FIXED_BOTTOM_OFFSET}>
        <Box maxW="280px">
          <img
            src={illustrationImg}
            alt="Análise de imagem dermatológica"
            style={{ width: "100%", height: "auto" }}
          />
        </Box>

        <Text
          textAlign="center"
          color={COLORS.blueText}
          fontSize="sm"
          lineHeight="tall"
          maxW="340px"
        >
          Escolha uma foto da galeria ou tire uma nova fotografia da área da
          pele que deseja analisar. A inteligência artificial verificará a
          presença de sinais sugestivos de hanseníase.
        </Text>

        <Stack w="100%" maxW="400px" gap={4}>
          <DashedActionButton
            icon={<Camera size={20} />}
            label="Tirar Foto"
            onClick={() => cameraInputRef.current?.click()}
          />
          <DashedActionButton
            icon={<ImageIcon size={20} />}
            label="Escolher da Galeria"
            onClick={() => fileInputRef.current?.click()}
          />
        </Stack>
      </Stack>

      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        hidden
        onChange={(e) => handleFileChange(e.target.files?.[0])}
      />
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        hidden
        onChange={(e) => handleFileChange(e.target.files?.[0])}
      />
    </Flex>
  )
}
