import { IconButton } from "@chakra-ui/react"
import { LogOut } from "lucide-react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../contexts/AuthContext"

export default function LogoutButton() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  if (!user) return null

  async function handleLogout() {
    try {
      await logout()
      navigate("/login", { replace: true })
    } catch {
      alert("Erro ao sair")
    }
  }

  return (
    <IconButton
      aria-label="Sair"
      position="fixed"
      top="20px"
      right="20px"
      variant="ghost"
      onClick={handleLogout}
      zIndex={1000}
    >
      <LogOut size={18} />
    </IconButton>
  )
}