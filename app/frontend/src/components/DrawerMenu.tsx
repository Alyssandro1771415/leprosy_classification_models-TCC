import { Flex, IconButton, Text } from "@chakra-ui/react"
import { AnimatePresence, motion } from "framer-motion"
import { ArrowLeft, Info, LogOut, User } from "lucide-react"
import { useNavigate } from "react-router-dom"

import { COLORS } from "../constants/colors"
import { useAuth } from "../contexts/AuthContext"
import { useDrawer } from "../contexts/DrawerContext"
import logoVertical from "../imagens_APP_TCC/2f5683dc6aa2cfa44d2dd862826ae7497965bdfe.png"

const menuItems = [
  { label: "Meus dados", icon: User, path: "/my-data" },
  { label: "Sobre o Projeto", icon: Info, path: "/about" },
]

export default function DrawerMenu() {
  const navigate = useNavigate()
  const { isOpen, closeDrawer } = useDrawer()
  const { logout } = useAuth()

  async function handleLogout() {
    try {
      await logout()
      closeDrawer()
      navigate("/login", { replace: true })
    } catch {
      alert("Erro ao sair")
    }
  }

  function navigateTo(path: string) {
    closeDrawer()
    navigate(path)
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: "fixed",
              inset: 0,
              background: "rgba(0,0,0,0.4)",
              zIndex: 1400,
            }}
            onClick={closeDrawer}
          />

          <motion.div
            initial={{ x: "-100%" }}
            animate={{ x: 0 }}
            exit={{ x: "-100%" }}
            transition={{ duration: 0.25 }}
            style={{
              position: "fixed",
              top: 0,
              left: 0,
              bottom: 0,
              width: "78%",
              maxWidth: "320px",
              background: "white",
              zIndex: 1500,
              boxShadow: "0 10px 40px rgba(0,0,0,0.15)",
              padding: "24px",
            }}
          >
            <IconButton
              aria-label="Fechar menu"
              variant="ghost"
              size="sm"
              color={COLORS.blueText}
              mb={8}
              onClick={closeDrawer}
              _hover={{ bg: "gray.100" }}
            >
              <ArrowLeft size={22} />
            </IconButton>

            <Flex justify="center" mb={10}>
              <img
                src={logoVertical}
                alt="leprosy IDENTIFIER"
                style={{ width: "160px", height: "auto" }}
              />
            </Flex>

            <Flex direction="column" gap={6}>
              {menuItems.map((item) => (
                <Flex
                  key={item.path}
                  align="center"
                  gap={4}
                  cursor="pointer"
                  color={COLORS.blueText}
                  onClick={() => navigateTo(item.path)}
                  _hover={{ opacity: 0.8 }}
                >
                  <item.icon size={22} color={COLORS.purple} />
                  <Text fontWeight="medium">{item.label}</Text>
                </Flex>
              ))}

              <Flex
                align="center"
                gap={4}
                cursor="pointer"
                color={COLORS.blueText}
                onClick={handleLogout}
                _hover={{ opacity: 0.8 }}
              >
                <LogOut size={22} color={COLORS.purple} />
                <Text fontWeight="medium">Sair</Text>
              </Flex>
            </Flex>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
