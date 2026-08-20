import io

import cv2
import numpy as np
import tensorflow as tf
from PIL import Image

TARGET_SIZE = (224, 224)


def apply_bilateral_filter(image_array: np.ndarray, d=9, sigma_color=75, sigma_space=75) -> np.ndarray:
    return cv2.bilateralFilter(image_array, d, sigma_color, sigma_space)


def rgb_to_y_bilateral(image: Image.Image) -> np.ndarray:
    """RGB → canal Y → bilateral → normalizado [0, 1], shape (H, W)."""
    ycbcr = image.convert("YCbCr")
    y, _, _ = ycbcr.split()
    y_array = np.array(y, dtype=np.uint8)
    y_array = apply_bilateral_filter(y_array)
    return y_array.astype(np.float32) / 255.0


def resize_y_channel(y_channel: np.ndarray) -> np.ndarray:
    resized = tf.image.resize(
        y_channel[..., np.newaxis],
        TARGET_SIZE,
        method="bilinear",
    ).numpy()
    return np.squeeze(resized, axis=-1)


def open_rgb_image(image_bytes: bytes) -> Image.Image:
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")


def prepare_model_input(image_bytes: bytes) -> np.ndarray:
    """Retorna tensor (1, 224, 224, 1) pronto para o modelo from-zero."""
    image = open_rgb_image(image_bytes)
    y_channel = rgb_to_y_bilateral(image)
    y_channel = resize_y_channel(y_channel)
    return np.expand_dims(y_channel, axis=(0, -1)).astype(np.float32)


def prepare_model_input_dict(image_bytes: bytes) -> np.ndarray:
    """Tensor (1, 224, 224, 1) — compatível com InputLayer `input_1` do modelo y_bilateral."""
    return prepare_model_input(image_bytes)


def y_channel_to_display_rgb(y_channel: np.ndarray) -> np.ndarray:
    """Converte canal Y em RGB uint8 para exibição."""
    values = np.clip(y_channel * 255.0, 0, 255).astype(np.uint8)
    return np.stack([values, values, values], axis=-1)


def y_channel_to_png_bytes(y_channel: np.ndarray) -> bytes:
    rgb = y_channel_to_display_rgb(y_channel)
    image = Image.fromarray(rgb)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def prepare_preprocessed_png(image_bytes: bytes) -> bytes:
    image = open_rgb_image(image_bytes)
    y_channel = rgb_to_y_bilateral(image)
    y_channel = resize_y_channel(y_channel)
    return y_channel_to_png_bytes(y_channel)
