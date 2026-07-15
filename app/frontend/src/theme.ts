import { createSystem, defaultConfig, defineConfig } from "@chakra-ui/react"

const customConfig = defineConfig({
  globalCss: {
    html: {
      colorScheme: "light",
      bg: "#FFFFFF",
    },
    body: {
      bg: "#FFFFFF",
      color: "#3B4568",
    },
    "#root": {
      bg: "#FFFFFF",
      minH: "100dvh",
    },
  },
})

export const system = createSystem(defaultConfig, customConfig)
