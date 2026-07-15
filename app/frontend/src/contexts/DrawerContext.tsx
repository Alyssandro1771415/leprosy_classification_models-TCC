import { createContext, useContext, useState, type ReactNode } from "react"

type DrawerContextType = {
  isOpen: boolean
  openDrawer: () => void
  closeDrawer: () => void
}

const DrawerContext = createContext<DrawerContextType | null>(null)

export function DrawerProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <DrawerContext.Provider
      value={{
        isOpen,
        openDrawer: () => setIsOpen(true),
        closeDrawer: () => setIsOpen(false),
      }}
    >
      {children}
    </DrawerContext.Provider>
  )
}

export function useDrawer() {
  const context = useContext(DrawerContext)
  if (!context) {
    throw new Error("useDrawer must be used within DrawerProvider")
  }
  return context
}
