from src.services.image_service import ImageService

class ImageController:

    def __init__(self):
        self.image_service = ImageService()

    def convert_file_to_base64(self, file_bytes: bytes) -> str:
        """Recebe os bytes do arquivo e retorna a string para salvar no banco."""
        return self.image_service.encode_to_base64(file_bytes)

    def prepare_image_for_processing(self, base64_string: str) -> bytes:
        """Recebe a string do banco e prepara os bytes para a IA/Processamento."""
        return self.image_service.decode_from_base64(base64_string)