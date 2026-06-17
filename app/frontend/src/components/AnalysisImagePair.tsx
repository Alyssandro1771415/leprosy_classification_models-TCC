import { Badge, Box, Grid, Heading, Image } from "@chakra-ui/react"

type AnalysisImagePairProps = {
  originalSrc: string
  preprocessedSrc?: string | null
  focusSrc?: string | null
  loadingFocus?: boolean
}

function ImagePanel({
  title,
  src,
  alt,
  placeholder,
}: {
  title: string
  src?: string | null
  alt: string
  placeholder?: string
}) {
  return (
    <Box>
      <Heading size="sm" mb={3}>
        {title}
      </Heading>
      {src ? (
        <Image
          src={src}
          alt={alt}
          borderRadius="lg"
          objectFit="contain"
          w="100%"
          maxH="360px"
          bg="gray.50"
        />
      ) : (
        <Box
          borderRadius="lg"
          bg="gray.50"
          h="360px"
          display="flex"
          alignItems="center"
          justifyContent="center"
          color="gray.500"
          fontSize="sm"
          textAlign="center"
          px={4}
        >
          {placeholder}
        </Box>
      )}
    </Box>
  )
}

export default function AnalysisImagePair({
  originalSrc,
  preprocessedSrc,
  focusSrc,
  loadingFocus = false,
}: AnalysisImagePairProps) {
  const columns = preprocessedSrc || loadingFocus ? { base: "1fr", md: "repeat(3, 1fr)" } : { base: "1fr", md: "1fr 1fr" }

  return (
    <Grid templateColumns={columns} gap={6}>
      <ImagePanel
        title="Imagem Original"
        src={originalSrc}
        alt="Imagem original enviada para classificação"
      />

      {(preprocessedSrc || loadingFocus) && (
        <ImagePanel
          title="Pré-processamento (Canal Y + Bilateral)"
          src={preprocessedSrc}
          alt="Imagem após extração do canal Y e filtro bilateral"
          placeholder="Gerando pré-processamento..."
        />
      )}

      <Box>
        <Heading size="sm" mb={3}>
          Mapa de Calor (Grad-CAM)
        </Heading>
        {loadingFocus ? (
          <Box
            borderRadius="lg"
            bg="gray.50"
            h="360px"
            display="flex"
            alignItems="center"
            justifyContent="center"
            color="gray.500"
            fontSize="sm"
          >
            Gerando mapa de calor...
          </Box>
        ) : focusSrc ? (
          <>
            <Image
              src={focusSrc}
              alt="Mapa de calor Grad-CAM sobre a imagem pré-processada"
              borderRadius="lg"
              objectFit="contain"
              w="100%"
              maxH="360px"
              bg="gray.50"
            />
            <Badge mt={3} colorScheme="teal">
              Grad-CAM
            </Badge>
          </>
        ) : (
          <Box
            borderRadius="lg"
            bg="gray.50"
            h="360px"
            display="flex"
            alignItems="center"
            justifyContent="center"
            color="gray.500"
            fontSize="sm"
            textAlign="center"
            px={4}
          >
            Não foi possível gerar o mapa de calor.
          </Box>
        )}
      </Box>
    </Grid>
  )
}
