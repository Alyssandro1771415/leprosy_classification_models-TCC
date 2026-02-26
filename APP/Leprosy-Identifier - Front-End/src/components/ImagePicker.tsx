import {
  Box,
  Icon,
  Text,
  VStack,
  HStack,
  Button,
  Dialog,
  Portal,
} from "@chakra-ui/react"
import { FiCamera, FiImage } from "react-icons/fi"
import { useRef, useState } from "react"
import { useNavigate } from "react-router-dom"

export default function ImagePicker() {
  const navigate = useNavigate()

  const [open, setOpen] = useState(false)

  const cameraInputRef = useRef<HTMLInputElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  function handleCamera() {
    setOpen(false)
    cameraInputRef.current?.click()
  }

  function handleFile() {
    setOpen(false)
    fileInputRef.current?.click()
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]

    if (file) {
      const imageUrl = URL.createObjectURL(file)

      navigate("/analyze", {
        state: {
          file,
          preview: imageUrl,
        },
      })
    }
  }

  return (
    <>
      <Box
        border="2px dashed"
        borderColor="border"
        bg="bg.surface"
        _hover={{ bg: "bg.muted" }}
        borderRadius="xl"
        p={10}
        textAlign="center"
        cursor="pointer"
        onClick={() => setOpen(true)}
      >
        <VStack>
          <Icon as={FiCamera} boxSize={10} color="fg.muted" />
          <Text fontSize="lg" fontWeight="medium">
            Carregar foto
          </Text>
        </VStack>
      </Box>

      <Dialog.Root open={open} onOpenChange={(e) => setOpen(e.open)}>
        <Portal>
          <Dialog.Backdrop />
          <Dialog.Positioner>
            <Dialog.Content borderRadius="2xl">
              <Dialog.Header>
                <Dialog.Title>Selecionar imagem</Dialog.Title>
              </Dialog.Header>

              <Dialog.Body>
                <HStack justify="space-between">
                  <Button
                    onClick={handleCamera}
                    flex={1}
                    h="120px"
                    variant="outline"
                  >
                    <VStack>
                      <Icon as={FiCamera} boxSize={8} />
                      <Text>Câmera</Text>
                    </VStack>
                  </Button>

                  <Button
                    onClick={handleFile}
                    flex={1}
                    h="120px"
                    variant="outline"
                  >
                    <VStack>
                      <Icon as={FiImage} boxSize={8} />
                      <Text>Arquivo</Text>
                    </VStack>
                  </Button>
                </HStack>
              </Dialog.Body>
            </Dialog.Content>
          </Dialog.Positioner>
        </Portal>
      </Dialog.Root>

      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        hidden
        onChange={handleFileChange}
      />

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        hidden
        onChange={handleFileChange}
      />
    </>
  )
}