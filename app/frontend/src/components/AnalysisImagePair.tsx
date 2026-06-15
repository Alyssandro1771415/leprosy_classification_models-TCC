import { Badge, Box, Grid, Heading, Image } from "@chakra-ui/react"

type AnalysisImagePairProps = {
  originalSrc: string
  focusSrc?: string | null
  loadingFocus?: boolean
}

export default function AnalysisImagePair({
  originalSrc,
  focusSrc,
  loadingFocus = false,
}: AnalysisImagePairProps) {
  return (
    <Grid templateColumns={{ base: "1fr", md: "1fr 1fr" }} gap={6}>
      <Box>
        <Heading size="sm" mb={3}>
          Imagem Original
        </Heading>
        <Image
          src={originalSrc}
          alt="Imagem original enviada para classificação"
          borderRadius="lg"
          objectFit="contain"
          w="100%"
          maxH="360px"
          bg="gray.50"
        />
      </Box>

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
              alt="Mapa de calor Grad-CAM sobre a imagem analisada"
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
