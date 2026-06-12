import { Box, Flex, Icon, Text } from "@chakra-ui/react"
import { FiHome, FiCamera, FiInfo } from "react-icons/fi"
import { useNavigate, useLocation } from "react-router-dom"

const navItems = [
  { label: "Home", icon: FiHome, path: "/home" },
  { label: "Analisar", icon: FiCamera, path: "/analyze" },
  { label: "Sobre", icon: FiInfo, path: "/about" },
]

export default function BottomNav() {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <Box
      position="fixed"
      bottom="0"
      w="90%"
      left="50%"
      transform="translateX(-50%)"
      bg="rgba(255, 255, 255, 0.08)"
      backdropFilter="blur(12px)"
      borderTop="1px solid"
      borderColor="border"
      py={2}
      px={4}
      mb={12}
      zIndex="1000"
      borderRadius={8}
    >
      <Flex justify="space-around" align="center">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path

          return (
            <Flex
              key={item.path}
              direction="column"
              align="center"
              justify="center"
              cursor="pointer"
              color={isActive ? "teal.500" : "fg.muted"}
              onClick={() => navigate(item.path)}
            >
              <Icon as={item.icon} boxSize={6} />
              <Text fontSize="xs">{item.label}</Text>
            </Flex>
          )
        })}
      </Flex>
    </Box>
  )
}