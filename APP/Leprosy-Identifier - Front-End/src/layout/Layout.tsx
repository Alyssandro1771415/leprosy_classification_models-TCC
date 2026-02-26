import { Flex, Box } from "@chakra-ui/react"
import { Outlet } from "react-router-dom"
import BottomNav from "../components/BottomNav"

export default function Layout() {
  return (
    <Flex direction="column" minH="100vh">
      <Box flex="1" pb="70px">
        <Outlet />
      </Box>

      <BottomNav />
    </Flex>
  )
}