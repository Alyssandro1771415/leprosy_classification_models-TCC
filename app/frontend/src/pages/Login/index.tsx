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
import { useState } from "react"
import { useAuth } from "../../contexts/AuthContext"

import { type UserCredential } from "firebase/auth";

import logo_header from "../../assets/logo_header.png"

export default function Login() {
  const navigate = useNavigate()
  const { login, loginWithGoogle } = useAuth()

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleLogin() {
    try {
      setLoading(true)
      await login(email, password)
      navigate("/home")
    } catch (error) {
      alert("Email ou senha inválidos")
    } finally {
      setLoading(false)
    }
  }

  async function handleGoogleLogin() {
    try {
      setLoading(true);

      const result = await loginWithGoogle() as UserCredential;
      const user = result.user;

      await fetch(`${import.meta.env.API_LINK}/users/consent/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-access-token": import.meta.env.VITE_SECRET_TOKEN
        },
        body: JSON.stringify({
          user_id: user.uid,
          email: user.email,
          name: user.displayName,
          allow: true
        }),
      });

      navigate("/home");
    } catch (error) {
      console.error(error);
      alert("Erro no login ou sincronização");
    } finally {
      setLoading(false);
    }
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
              placeholder="Email"
              size="lg"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              bg="bg.muted"
              border="1px solid"
              borderColor="border"
            />

            <Input
              placeholder="Senha"
              type="password"
              size="lg"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              bg="bg.muted"
              border="1px solid"
              borderColor="border"
            />
          </Stack>

          <Button
            size="lg"
            colorScheme="teal"
            onClick={handleLogin}
            loading={loading}
          >
            Entrar
          </Button>

          <Button
            size="lg"
            variant="outline"
            onClick={handleGoogleLogin}
            loading={loading}
          >
            Entrar com Google
          </Button>

          <Text
            textAlign="center"
            fontSize="sm"
            color="fg.muted"
            cursor="pointer"
            onClick={() => navigate("/register")}
          >
            Criar conta
          </Text>

          <Text textAlign="center" fontSize="xs" color="fg.muted">
            Leprosy Identifier
          </Text>
        </Stack>
      </Box>
    </Flex>
  )
}