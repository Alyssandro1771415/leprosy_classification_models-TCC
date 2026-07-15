import { Button, Flex, Text } from "@chakra-ui/react"
import type { ReactNode } from "react"

import { COLORS } from "../constants/colors"

type DashedActionButtonProps = {
  icon: ReactNode
  label: string
  onClick: () => void
}

export default function DashedActionButton({
  icon,
  label,
  onClick,
}: DashedActionButtonProps) {
  return (
    <Button
      w="100%"
      h="56px"
      variant="outline"
      borderStyle="dashed"
      borderWidth="2px"
      borderColor={COLORS.purple}
      borderRadius="12px"
      color={COLORS.purple}
      fontWeight="bold"
      bg="white"
      onClick={onClick}
      _hover={{ bg: "gray.50" }}
    >
      <Flex align="center" gap={3}>
        {icon}
        <Text textTransform="none" fontWeight="bold">
          {label}
        </Text>
      </Flex>
    </Button>
  )
}

export function PrimaryActionButton({
  children,
  onClick,
  loading,
}: {
  children: ReactNode
  onClick: () => void
  loading?: boolean
}) {
  return (
    <Button
      w="100%"
      h="52px"
      bg={COLORS.purple}
      color="white"
      borderRadius="12px"
      fontWeight="bold"
      letterSpacing="wider"
      textTransform="uppercase"
      onClick={onClick}
      loading={loading}
      _hover={{ bg: "#351049" }}
    >
      {children}
    </Button>
  )
}

export function OutlineActionButton({
  children,
  onClick,
  loading,
}: {
  children: ReactNode
  onClick: () => void
  loading?: boolean
}) {
  return (
    <Button
      w="100%"
      h="52px"
      variant="outline"
      borderColor={COLORS.purple}
      borderWidth="2px"
      color={COLORS.purple}
      borderRadius="12px"
      fontWeight="bold"
      letterSpacing="wider"
      textTransform="uppercase"
      onClick={onClick}
      loading={loading}
      _hover={{ bg: "gray.50" }}
    >
      {children}
    </Button>
  )
}
