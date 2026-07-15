import {
  Box,
  Button,
  Flex,
  Input,
  Stack,
  Text,
} from "@chakra-ui/react"
import { useState } from "react"
import { useNavigate } from "react-router-dom"

import { COLORS } from "../../constants/colors"
import { useAuth } from "../../contexts/AuthContext"
import logoVertical from "../../imagens_APP_TCC/2f5683dc6aa2cfa44d2dd862826ae7497965bdfe.png"

const inputStyles = {
  bg: "#EBEBEB",
  border: "none",
  borderRadius: "10px",
  h: "48px",
  color: COLORS.blueText,
  fontSize: "sm",
  _focus: {
    outline: "2px solid",
    outlineColor: COLORS.purple,
    outlineOffset: "0",
  },
}

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleRegister() {
    try {
      setLoading(true)
      await register(email, password)
      navigate("/home")
    } catch {
      alert("Erro ao cadastrar")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Flex direction="column" minH="100dvh" bg="white" px={6} py={8}>
      <Flex flex="1" direction="column" justify="center" w="100%" maxW="400px" mx="auto">
        <Flex justify="center" mb={10}>
          <img
            src={logoVertical}
            alt="leprosy IDENTIFIER"
            style={{ width: "180px", height: "auto" }}
          />
        </Flex>

        <Text
          textAlign="center"
          color={COLORS.blueText}
          fontWeight="bold"
          fontSize="lg"
          mb={6}
        >
          Criar Conta
        </Text>

        <Stack gap={5}>
          <Box>
            <Text color={COLORS.blueText} fontSize="sm" fontWeight="medium" mb={2}>
              E-mail
            </Text>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              {...inputStyles}
            />
          </Box>

          <Box>
            <Text color={COLORS.blueText} fontSize="sm" fontWeight="medium" mb={2}>
              Senha
            </Text>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              {...inputStyles}
            />
          </Box>

          <Button
            w="100%"
            h="48px"
            bg={COLORS.purple}
            color="white"
            borderRadius="10px"
            fontWeight="bold"
            letterSpacing="wider"
            textTransform="uppercase"
            onClick={handleRegister}
            loading={loading}
            mt={2}
            _hover={{ bg: "#351049" }}
          >
            Cadastrar
          </Button>

          <Text
            textAlign="center"
            color={COLORS.purple}
            fontSize="sm"
            fontWeight="bold"
            cursor="pointer"
            onClick={() => navigate("/login")}
          >
            Já tenho conta
          </Text>
        </Stack>
      </Flex>
    </Flex>
  )
}
