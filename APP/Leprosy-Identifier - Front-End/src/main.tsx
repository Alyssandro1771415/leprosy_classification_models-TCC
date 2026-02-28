import React from "react"
import ReactDOM from "react-dom/client"
import App from "./App.tsx"

import { ChakraProvider } from "@chakra-ui/react"
import { ThemeProvider } from "next-themes"
import { system } from "./theme"

import { AuthProvider } from "./contexts/AuthContext.tsx"

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ChakraProvider value={system}>
      <ThemeProvider attribute="class" defaultTheme="dark">
        <AuthProvider>
          <App />
        </AuthProvider>
      </ThemeProvider>
    </ChakraProvider>
  </React.StrictMode>
)