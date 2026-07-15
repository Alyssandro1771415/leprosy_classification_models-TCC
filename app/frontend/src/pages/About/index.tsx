import { Box, Flex, Stack, Text } from "@chakra-ui/react"

import { PageHeader } from "../../components/PageHeader"
import { COLORS } from "../../constants/colors"
import { FIXED_BOTTOM_OFFSET } from "../../constants/layout"
import aboutIllustration from "../../imagens_APP_TCC/b39ebb834ce41fb9bbe9914ab4ab5978bb316088.png"

const sections = [
  {
    title: "Leprosy Identifier",
    body: "Aplicação desenvolvida para auxiliar na triagem de hanseníase por meio de modelos de inteligência artificial aplicados a imagens dermatológicas.",
  },
  {
    title: "Como funciona?",
    body: "A imagem enviada é processada por um modelo de deep learning treinado para identificar padrões associados à doença.",
  },
  {
    title: "Objetivo",
    body: "Fornecer uma ferramenta de apoio ao diagnóstico, contribuindo para detecção precoce e tomada de decisão clínica.",
  },
  {
    title: "Desenvolvedor",
    body: "Alyssandro Ramos",
  },
]

export default function About() {
  return (
    <Flex
      direction="column"
      minH="100dvh"
      bg={COLORS.pageBg}
      align="center"
      color={COLORS.blueText}
    >
      <Box
        w="100%"
        maxW="430px"
        minH="100dvh"
        display="flex"
        flexDirection="column"
        bg={COLORS.pageBg}
      >
        <PageHeader title="Sobre o Projeto" backTo="/home" />

        <Flex
          flex="1"
          direction="column"
          justify="flex-end"
          minH={0}
        >
          <Flex
            flex="1"
            align="center"
            justify="center"
            px="24px"
            pt="8px"
            pb="16px"
            minH="34vh"
          >
            <img
              src={aboutIllustration}
              alt="Ilustração do projeto Leprosy Identifier"
              style={{
                width: "288px",
                height: "350px",
                display: "block",
              }}
            />
          </Flex>

          <Stack px="22px" pb={FIXED_BOTTOM_OFFSET} gap="26px" flexShrink={0}>
            {sections.map((section) => (
              <Box key={section.title}>
                <Text
                  fontWeight="bold"
                  fontSize="16px"
                  mb="8px"
                  color={COLORS.blueText}
                  lineHeight="1.3"
                >
                  {section.title}
                </Text>
                <Text
                  fontWeight="normal"
                  fontSize="15px"
                  lineHeight="1.55"
                  color={COLORS.blueText}
                >
                  {section.body}
                </Text>
              </Box>
            ))}
          </Stack>
        </Flex>
      </Box>
    </Flex>
  )
}
