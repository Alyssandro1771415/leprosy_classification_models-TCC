import {
  Box,
  Button,
  Flex,
  Input,
  Stack,
  Text,
} from "@chakra-ui/react"
import {
  browserLocalPersistence,
  browserSessionPersistence,
  setPersistence,
  type UserCredential,
} from "firebase/auth"
import { Capacitor } from "@capacitor/core"
import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

import { getApiBaseUrl } from "../../config/api"
import { COLORS } from "../../constants/colors"
import { useAuth } from "../../contexts/AuthContext"
import { auth } from "../../services/firebase"
import logoVertical from "../../imagens_APP_TCC/2f5683dc6aa2cfa44d2dd862826ae7497965bdfe.png"

function GoogleIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="#4285F4"
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
      />
      <path
        fill="#34A853"
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
      />
      <path
        fill="#FBBC05"
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
      />
      <path
        fill="#EA4335"
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
      />
    </svg>
  )
}

const inputStyles = {
  bg: "#EBEBEB",
  border: "none",
  borderRadius: "10px",
  h: "48px",
  color: COLORS.blueText,
  fontSize: "sm",
  _placeholder: { color: "gray.400" },
  _focus: {
    outline: "2px solid",
    outlineColor: COLORS.purple,
    outlineOffset: "0",
  },
}

export default function Login() {
  const navigate = useNavigate()
  const { user, login, loginWithGoogle } = useAuth()

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [keepConnected, setKeepConnected] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (user) {
      navigate("/home", { replace: true })
    }
  }, [user, navigate])

  async function applyPersistence() {
    if (Capacitor.isNativePlatform()) return

    await setPersistence(
      auth,
      keepConnected ? browserLocalPersistence : browserSessionPersistence,
    )
  }

  async function handleLogin() {
    try {
      setLoading(true)
      await applyPersistence()
      await login(email, password)
      navigate("/home")
    } catch {
      alert("Email ou senha inválidos")
    } finally {
      setLoading(false)
    }
  }

  async function handleGoogleLogin() {
    try {
      setLoading(true)
      await applyPersistence()

      const result = (await loginWithGoogle()) as UserCredential
      const googleUser = result.user

      try {
        const response = await fetch(`${getApiBaseUrl()}/users/consent/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "x-access-token": import.meta.env.VITE_SECRET_TOKEN,
          },
          body: JSON.stringify({
            user_id: googleUser.uid,
            email: googleUser.email,
            name: googleUser.displayName,
            allow: true,
          }),
        })

        if (!response.ok) {
          console.warn("Sincronização de consentimento falhou:", response.status)
        }
      } catch (syncError) {
        console.warn("Sincronização de consentimento indisponível:", syncError)
      }

      navigate("/home")
    } catch (error) {
      console.error(error)
      alert("Erro no login com Google")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Flex
      direction="column"
      minH="100dvh"
      bg="white"
      px={6}
      py={8}
    >
      <Flex flex="1" direction="column" justify="center" w="100%" maxW="400px" mx="auto">
        <Flex justify="center" mb={10}>
          <img
            src={logoVertical}
            alt="leprosy IDENTIFIER"
            style={{
              width: "200px",
              height: "auto",
              display: "block",
            }}
          />
        </Flex>

        <Stack gap={5}>
          <Box>
            <Text color={COLORS.blueText} fontSize="sm" fontWeight="medium" mb={2}>
              Usuário
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

          <Stack gap={2}>
            <Flex as="label" align="center" gap={2} cursor="pointer" w="fit-content">
              <input
                type="checkbox"
                checked={keepConnected}
                onChange={(e) => setKeepConnected(e.target.checked)}
                style={{
                  width: "16px",
                  height: "16px",
                  accentColor: COLORS.purple,
                  cursor: "pointer",
                }}
              />
              <Text color={COLORS.blueText} fontSize="sm">
                Manter-me conectado
              </Text>
            </Flex>

            <Text
              color={COLORS.blueText}
              fontSize="sm"
              cursor="pointer"
              w="fit-content"
              onClick={() => alert("Funcionalidade em desenvolvimento")}
            >
              Esqueci minha senha
            </Text>
          </Stack>

          <Stack gap={3} mt={2}>
            <Button
              w="100%"
              h="48px"
              bg={COLORS.purple}
              color="white"
              borderRadius="10px"
              fontWeight="bold"
              letterSpacing="wider"
              textTransform="uppercase"
              onClick={handleLogin}
              loading={loading}
              _hover={{ bg: "#351049" }}
            >
              Entrar
            </Button>

            <Button
              w="100%"
              h="48px"
              variant="outline"
              borderColor={COLORS.purple}
              borderWidth="2px"
              color={COLORS.purple}
              borderRadius="10px"
              fontWeight="bold"
              letterSpacing="wider"
              textTransform="uppercase"
              onClick={handleGoogleLogin}
              loading={loading}
              _hover={{ bg: "gray.50" }}
            >
              <Flex align="center" gap={3}>
                <GoogleIcon />
                Entrar com Google
              </Flex>
            </Button>

            <Button
              variant="ghost"
              color={COLORS.purple}
              fontWeight="bold"
              letterSpacing="wider"
              textTransform="uppercase"
              onClick={() => navigate("/register")}
              _hover={{ bg: "transparent", opacity: 0.8 }}
            >
              Criar conta
            </Button>
          </Stack>
        </Stack>
      </Flex>

      <Stack gap={1} pt={8} pb={2}>
        <Text textAlign="center" fontSize="xs" color="gray.400">
          2026 - Leprosy Identifier
        </Text>
        <Text textAlign="center" fontSize="xs" color="gray.400">
          Desenvolvido por Alyssandro Ramos
        </Text>
      </Stack>
    </Flex>
  )
}
