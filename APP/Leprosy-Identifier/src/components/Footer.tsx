import {
  Box,
  Container,
  Flex,
  HStack,
  IconButton,
  Image,
  Link,
  Text,
  VStack,
  Separator,
} from "@chakra-ui/react"

import { FiLinkedin } from "react-icons/fi"

import logo from "../assets/logo_header.png"

export default function Footer() {
  return (
    <Box bg="bg.surface" borderTop="1px solid" borderColor="border" mt={10} mb={5}>
      <Container maxW="6xl" py={10}>
        <Flex
          direction={{ base: "column", md: "row" }}
          align="center"
          justify="space-between"
          gap={8}
        >
          <VStack align={{ base: "center", md: "start" }} maxW="400px">
            <Image src={logo} boxSize="200px" alt="Logo" />

            <Text textAlign={{ base: "center", md: "left" }} color="fg.muted">
              Onde a IA auxilia na identificação precoce através da análise de
              imagens.
            </Text>
          </VStack>

          <HStack>
            <IconButton variant="ghost" size="lg" aria-label="Linkedin" asChild>
              <Link href="https://www.linkedin.com/in/alyssandro-ramos-9672331ba/" target="_blank">
                <FiLinkedin />
              </Link>
            </IconButton>
          </HStack>
        </Flex>

        <Separator my={6} />

        <Flex
          direction={{ base: "column", md: "row" }}
          justify="space-between"
          align="center"
          gap={2}
        >
          <Text fontSize="sm" color="fg.muted">
            © 2026 — Leprosy Identifier
          </Text>

          <Text fontSize="sm" color="fg.muted">
            Desenvolvido por{" "}
            <Link
              href="https://www.linkedin.com"
              target="_blank"
              fontWeight="bold"
            >
              Alyssandro Ramos
            </Link>
          </Text>
        </Flex>
      </Container>
    </Box>
  )
}