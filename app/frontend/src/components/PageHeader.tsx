import { Box, Flex, IconButton, Text } from "@chakra-ui/react"
import { ArrowLeft } from "lucide-react"
import { useNavigate } from "react-router-dom"
import type { ReactNode } from "react"

import { COLORS } from "../constants/colors"
import { useDrawer } from "../contexts/DrawerContext"
import { FiMenu } from "react-icons/fi"

type PageHeaderProps = {
  title: string
  backTo?: string
  showMenu?: boolean
  rightAction?: ReactNode
}

export function PageHeader({
  title,
  backTo,
  showMenu = false,
  rightAction,
}: PageHeaderProps) {
  const navigate = useNavigate()
  const { openDrawer } = useDrawer()

  return (
    <Flex align="center" px={4} py={5} position="relative">
      {showMenu ? (
        <IconButton
          aria-label="Abrir menu"
          variant="ghost"
          size="md"
          color={COLORS.blueText}
          onClick={openDrawer}
          _hover={{ bg: "gray.100" }}
        >
          <FiMenu size={24} />
        </IconButton>
      ) : (
        <IconButton
          aria-label="Voltar"
          variant="ghost"
          size="md"
          minW="44px"
          h="44px"
          color={COLORS.blueText}
          onClick={() => (backTo ? navigate(backTo) : navigate(-1))}
          _hover={{ bg: "gray.100" }}
        >
          <ArrowLeft size={28} strokeWidth={2.5} />
        </IconButton>
      )}

      <Text
        position="absolute"
        left="50%"
        transform="translateX(-50%)"
        color={COLORS.blueText}
        fontWeight="bold"
        fontSize="lg"
        whiteSpace="nowrap"
      >
        {title}
      </Text>

      <Box ml="auto" minW="44px" display="flex" justifyContent="flex-end">
        {rightAction ?? <Box w="44px" />}
      </Box>
    </Flex>
  )
}
