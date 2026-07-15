import { Flex } from "@chakra-ui/react"
import { AnimatePresence, motion } from "framer-motion"
import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

import { COLORS } from "../../constants/colors"
import emblemImg from "../../imagens_APP_TCC/dc8d1f5247dabbda293bb7c53068ee5f1121059c.png"
import logoFullImg from "../../imagens_APP_TCC/8d3d7dc72fbfb64940f19ed4cdd8d3140263c3c0.png"

const EMBLEM_DURATION_MS = 1500
const LOGO_DURATION_MS = 2000

type SplashPhase = "emblem" | "logo"

function SplashImage({ src, alt, width }: { src: string; alt: string; width: string }) {
  return (
    <img
      src={src}
      alt={alt}
      style={{
        width,
        height: "auto",
        display: "block",
        mixBlendMode: "screen",
      }}
    />
  )
}

export default function Splash() {
  const [phase, setPhase] = useState<SplashPhase>("emblem")
  const navigate = useNavigate()

  useEffect(() => {
    const toLogoTimer = window.setTimeout(() => setPhase("logo"), EMBLEM_DURATION_MS)
    const toLoginTimer = window.setTimeout(
      () => navigate("/login", { replace: true }),
      EMBLEM_DURATION_MS + LOGO_DURATION_MS,
    )

    return () => {
      window.clearTimeout(toLogoTimer)
      window.clearTimeout(toLoginTimer)
    }
  }, [navigate])

  return (
    <Flex
      minH="100dvh"
      w="100vw"
      bg={COLORS.purple}
      align="center"
      justify="center"
      overflow="hidden"
    >
      <AnimatePresence mode="wait">
        {phase === "emblem" ? (
          <motion.div
            key="emblem"
            initial={{ opacity: 0, scale: 0.85 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.02 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          >
            <SplashImage src={emblemImg} alt="Leprosy Identifier" width="200px" />
          </motion.div>
        ) : (
          <motion.div
            key="logo"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: "easeOut" }}
          >
            <SplashImage src={logoFullImg} alt="leprosy IDENTIFIER" width="260px" />
          </motion.div>
        )}
      </AnimatePresence>
    </Flex>
  )
}
