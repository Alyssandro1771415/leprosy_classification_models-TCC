import { Box, Flex, IconButton, Image, Text } from "@chakra-ui/react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { useState } from "react"

import { COLORS } from "../constants/colors"

export type CarouselSlide = {
  src: string
  label: string
}

type ImageCarouselProps = {
  slides: CarouselSlide[]
  loading?: boolean
  imageFit?: "contain" | "cover"
}

export default function ImageCarousel({
  slides,
  loading,
  imageFit = "contain",
}: ImageCarouselProps) {
  const [index, setIndex] = useState(0)
  const validSlides = slides.filter((slide) => slide.src)

  const current = validSlides[index] ?? validSlides[0]

  function goPrev() {
    setIndex((prev) => (prev === 0 ? validSlides.length - 1 : prev - 1))
  }

  function goNext() {
    setIndex((prev) => (prev === validSlides.length - 1 ? 0 : prev + 1))
  }

  if (loading) {
    return (
      <Box textAlign="center" py={10}>
        <Text color="gray.400" fontSize="sm">
          Carregando visualizações...
        </Text>
      </Box>
    )
  }

  if (!current) {
    return (
      <Box textAlign="center" py={10}>
        <Text color="gray.400" fontSize="sm">
          Nenhuma imagem disponível.
        </Text>
      </Box>
    )
  }

  return (
    <Box>
      <Box position="relative">
        <Image
          src={current.src}
          alt={current.label}
          w="100%"
          h={imageFit === "cover" ? "240px" : "auto"}
          maxH={imageFit === "cover" ? "240px" : "280px"}
          objectFit={imageFit}
          borderRadius="16px"
          bg={imageFit === "cover" ? "#F0F0F0" : "#F5F5F5"}
        />

        {validSlides.length > 1 && (
          <>
            <IconButton
              aria-label="Imagem anterior"
              position="absolute"
              left={3}
              top="50%"
              transform="translateY(-50%)"
              size="sm"
              borderRadius="full"
              bg="white"
              color={COLORS.blueText}
              boxShadow="sm"
              onClick={goPrev}
            >
              <ChevronLeft size={20} />
            </IconButton>

            <IconButton
              aria-label="Próxima imagem"
              position="absolute"
              right={3}
              top="50%"
              transform="translateY(-50%)"
              size="sm"
              borderRadius="full"
              bg="white"
              color={COLORS.blueText}
              boxShadow="sm"
              onClick={goNext}
            >
              <ChevronRight size={20} />
            </IconButton>
          </>
        )}
      </Box>

      <Text
        textAlign="center"
        color={COLORS.blueText}
        fontSize="sm"
        fontWeight="medium"
        mt={3}
      >
        {current.label}
      </Text>

      {validSlides.length > 1 && (
        <Flex justify="center" gap={2} mt={3}>
          {validSlides.map((slide, slideIndex) => (
            <Box
              key={slide.label}
              w="8px"
              h="8px"
              borderRadius="full"
              bg={slideIndex === index ? COLORS.purple : "gray.300"}
              cursor="pointer"
              onClick={() => setIndex(slideIndex)}
            />
          ))}
        </Flex>
      )}
    </Box>
  )
}
