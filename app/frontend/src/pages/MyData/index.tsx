import { Box, Flex, Stack, Text } from "@chakra-ui/react"

import { PageHeader } from "../../components/PageHeader"
import { COLORS } from "../../constants/colors"
import { useAuth } from "../../contexts/AuthContext"

export default function MyData() {
  const { user } = useAuth()

  return (
    <Flex direction="column" minH="100dvh" bg="white">
      <PageHeader title="Meus Dados" backTo="/home" />

      <Stack flex="1" px={6} py={6} gap={6}>
        <Box bg="#F5F5F5" borderRadius="12px" p={4}>
          <Text color={COLORS.blueText} fontSize="xs" mb={1}>
            Nome
          </Text>
          <Text color={COLORS.blueText} fontWeight="bold">
            {user?.displayName ?? "—"}
          </Text>
        </Box>

        <Box bg="#F5F5F5" borderRadius="12px" p={4}>
          <Text color={COLORS.blueText} fontSize="xs" mb={1}>
            E-mail
          </Text>
          <Text color={COLORS.blueText} fontWeight="bold" wordBreak="break-all">
            {user?.email ?? "—"}
          </Text>
        </Box>

        <Box bg="#F5F5F5" borderRadius="12px" p={4}>
          <Text color={COLORS.blueText} fontSize="xs" mb={1}>
            ID do usuário
          </Text>
          <Text color={COLORS.blueText} fontWeight="bold" fontSize="sm" wordBreak="break-all">
            {user?.uid ?? "—"}
          </Text>
        </Box>
      </Stack>
    </Flex>
  )
}
