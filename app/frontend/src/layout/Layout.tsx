import { Box } from "@chakra-ui/react"
import { Outlet } from "react-router-dom"

import DrawerMenu from "../components/DrawerMenu"
import { COLORS } from "../constants/colors"
import { DrawerProvider } from "../contexts/DrawerContext"

export default function Layout() {
  return (
    <DrawerProvider>
      <Box minH="100dvh" bg={COLORS.pageBg}>
        <Outlet />
      </Box>
      <DrawerMenu />
    </DrawerProvider>
  )
}
