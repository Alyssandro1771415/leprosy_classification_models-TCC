import { Flex, Box, Heading } from "@chakra-ui/react"
import ImagePicker from "../../components/ImagePicker"

import logo_header from "../../assets/logo_header.png"

export default function Home() {
  return (
    <Flex minH="100vh" align="center" justify="center" px={6}>
      <Box w="100%" maxW="500px">
        <Heading size="lg" mb={6} textAlign="center">
          <img src={logo_header}></img>
        </Heading>

        <ImagePicker />
      </Box>
    </Flex>
  )
}