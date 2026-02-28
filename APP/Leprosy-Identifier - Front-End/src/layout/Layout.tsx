import { Flex, Box } from "@chakra-ui/react"
import { Outlet } from "react-router-dom"
import BottomNav from "../components/BottomNav"
import LogoutButton from "../components/LogOutButton"

export default function Layout() {
  return (
    <Flex direction="column" minH="100vh">
      <Box flex="1" pb="70px">
        <LogoutButton />
        <Outlet />
      </Box>

      <BottomNav />
    </Flex>
  )
}