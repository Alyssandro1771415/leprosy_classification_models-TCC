import {
  Flex,
  Box,
  Heading,
  Input,
  Button,
  Stack,
  Text,
} from "@chakra-ui/react"
import { useNavigate } from "react-router-dom"

import logo_header from "../../assets/logo_header.png"

export default function Login() {
  const navigate = useNavigate()

  function handleLogin() {
    navigate("/home")
  }

  return (
    <Flex
      minH="100vh"
      align="center"
      justify="center"
      bg="bg"
      px={4}
    >
      <Box
        w="100%"
        maxW="420px"
        p={10}
        borderRadius="2xl"
        bg="bg.panel"
        boxShadow="lg"
        border="1px solid"
        borderColor="border"
      >
        <Stack gap={6}>
          <Heading textAlign="center" size="lg">
            <img src={logo_header} alt="Logo" />
          </Heading>

          <Stack gap={4}>
            <Input
              placeholder="Usuário"
              size="lg"
              bg="bg.muted"
              border="1px solid"
              borderColor="border"
            />

            <Input
              placeholder="Senha"
              type="password"
              size="lg"
              bg="bg.muted"
              border="1px solid"
              borderColor="border"
            />
          </Stack>

          <Button
            size="lg"
            colorPalette="teal"
            onClick={handleLogin}
          >
            Entrar
          </Button>

          <Text textAlign="center" fontSize="sm" color="fg.muted">
            Leprosy Identifier
          </Text>
        </Stack>
      </Box>
    </Flex>
  )
}