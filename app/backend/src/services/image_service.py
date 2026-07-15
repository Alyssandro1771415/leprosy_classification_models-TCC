import base64
import io

from PIL import Image

# Firestore: string fields must stay under ~1 MiB; keep margin for other fields.
MAX_BASE64_LENGTH = 900_000
MAX_STORAGE_DIMENSION = 800
DEFAULT_JPEG_QUALITY = 72


class ImageService:

    def encode_to_base64(self, file_bytes: bytes) -> str:
        return self.encode_for_storage(file_bytes)

    def encode_for_storage(self, file_bytes: bytes) -> str:
        compressed = self._compress_image_bytes(file_bytes, DEFAULT_JPEG_QUALITY)
        encoded = base64.b64encode(compressed).decode("utf-8")

        quality = DEFAULT_JPEG_QUALITY
        while len(encoded) > MAX_BASE64_LENGTH and quality > 30:
            quality -= 10
            compressed = self._compress_image_bytes(file_bytes, quality)
            encoded = base64.b64encode(compressed).decode("utf-8")

        return encoded

    def compress_base64_for_storage(self, base64_string: str) -> str:
        return self.encode_for_storage(self.decode_from_base64(base64_string))

    def _compress_image_bytes(self, file_bytes: bytes, quality: int) -> bytes:
        image = Image.open(io.BytesIO(file_bytes))
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        elif image.mode == "L":
            image = image.convert("RGB")

        width, height = image.size
        max_dim = max(width, height)
        if max_dim > MAX_STORAGE_DIMENSION:
            scale = MAX_STORAGE_DIMENSION / max_dim
            image = image.resize(
                (int(width * scale), int(height * scale)),
                Image.Resampling.LANCZOS,
            )

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=quality, optimize=True)
        return buffer.getvalue()

    def decode_from_base64(self, base64_string: str) -> bytes:
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        return base64.b64decode(base64_string)

    def get_image_size_kb(self, base64_string: str) -> float:
        size_in_bytes = (len(base64_string) * 3) / 4
        return size_in_bytes / 1024