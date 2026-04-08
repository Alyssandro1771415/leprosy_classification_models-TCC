import base64
import io

class ImageService:

    def encode_to_base64(self, file_bytes: bytes) -> str:
        return base64.b64encode(file_bytes).decode("utf-8")

    def decode_from_base64(self, base64_string: str) -> bytes:
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        return base64.b64decode(base64_string)

    def get_image_size_kb(self, base64_string: str) -> float:
        size_in_bytes = (len(base64_string) * 3) / 4
        return size_in_bytes / 1024