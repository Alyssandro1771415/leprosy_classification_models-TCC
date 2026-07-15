import { Box, Flex, IconButton, Text } from "@chakra-ui/react"
import { FiMenu } from "react-icons/fi"

import { COLORS } from "../constants/colors"

type AppHeaderProps = {
  title: string
  onMenuClick?: () => void
}

export default function AppHeader({ title, onMenuClick }: AppHeaderProps) {
  return (
    <Flex align="center" px={4} py={4} position="relative">
      <IconButton
        aria-label="Abrir menu"
        variant="ghost"
        size="sm"
        color={COLORS.blueText}
        onClick={onMenuClick}
        _hover={{ bg: "gray.100" }}
      >
        <FiMenu size={22} />
      </IconButton>

      <Text
        position="absolute"
        left="50%"
        transform="translateX(-50%)"
        color={COLORS.blueText}
        fontWeight="bold"
        fontSize="md"
        whiteSpace="nowrap"
      >
        {title}
      </Text>

      <Box w="40px" />
    </Flex>
  )
}
