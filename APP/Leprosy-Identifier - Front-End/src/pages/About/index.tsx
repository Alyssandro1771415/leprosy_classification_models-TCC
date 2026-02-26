import {
  Container,
  Heading,
  Text,
  Stack,
  Box,
} from "@chakra-ui/react"

export default function About() {
  return (
    <Container py={8}>
      <Stack gap={6}>
        <Heading size="lg">Sobre o projeto</Heading>

        <Box>
          <Text fontWeight="bold">Leprosy Identifier</Text>
          <Text>
            Aplicação desenvolvida para auxiliar na triagem de
            hanseníase por meio de modelos de inteligência artificial
            aplicados a imagens dermatológicas.
          </Text>
        </Box>

        <Box>
          <Text fontWeight="bold">Como funciona?</Text>
          <Text>
            A imagem enviada é processada por um modelo de deep
            learning treinado para identificar padrões associados
            à doença.
          </Text>
        </Box>

        <Box>
          <Text fontWeight="bold">Objetivo</Text>
          <Text>
            Fornecer uma ferramenta de apoio ao diagnóstico,
            contribuindo para detecção precoce e tomada de decisão
            clínica.
          </Text>
        </Box>

        <Box>
          <Text fontWeight="bold">Desenvolvedor</Text>
          <Text>Alyssandro Ramos</Text>
        </Box>
      </Stack>
    </Container>
  )
}