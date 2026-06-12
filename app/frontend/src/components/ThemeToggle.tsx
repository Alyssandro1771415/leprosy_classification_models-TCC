import { useTheme } from "next-themes"
import { Button } from "@chakra-ui/react"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <Button
      onClick={() =>
        setTheme(theme === "dark" ? "light" : "dark")
      }
    >
      Alternar tema
    </Button>
  )
}