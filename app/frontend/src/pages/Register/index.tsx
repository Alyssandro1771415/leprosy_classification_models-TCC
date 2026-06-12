import {
  Button,
  Container,
  Heading,
  Input,
  Stack,
} from "@chakra-ui/react"
import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../../contexts/AuthContext"

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  async function handleRegister() {
    try {
      await register(email, password)
      navigate("/home")
    } catch {
      alert("Erro ao cadastrar")
    }
  }

  return (
    <Container py={10}>
      <Stack gap={6}>
        <Heading>Criar Conta</Heading>

        <Input
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <Input
          type="password"
          placeholder="Senha"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <Button colorScheme="teal" onClick={handleRegister}>
          Cadastrar
        </Button>
      </Stack>
    </Container>
  )
}