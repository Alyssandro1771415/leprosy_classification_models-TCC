import base64
import io

import cv2
import numpy as np
import tensorflow as tf
import tf_keras as keras
from PIL import Image

from src.services.preprocessing_service import (
    open_rgb_image,
    prepare_preprocessed_png,
    resize_y_channel,
    rgb_to_y_bilateral,
    y_channel_to_display_rgb,
)


class ModelFocusService:
    def __init__(self, model):
        self.model = model
        self.last_conv_layer_name = self._find_last_conv_layer_name()

    def generate_focus_result(self, image_bytes: bytes) -> dict:
        original_image = open_rgb_image(image_bytes)
        y_channel = resize_y_channel(rgb_to_y_bilateral(original_image))
        img_array = np.expand_dims(y_channel, axis=(0, -1)).astype(np.float32)

        heatmap = self._make_gradcam_heatmap(img_array)
        preprocessed_rgb = y_channel_to_display_rgb(y_channel)
        focused_image = self._overlay_heatmap(preprocessed_rgb, heatmap)

        return {
            "preprocessed_base64": base64.b64encode(
                prepare_preprocessed_png(image_bytes)
            ).decode("utf-8"),
            "focus_base64": self._image_to_base64(focused_image),
            "mime_type": "image/png",
        }

    def _image_to_base64(self, image: Image.Image) -> str:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def _make_gradcam_heatmap(self, img_array, pred_index=None):
        grad_model = keras.models.Model(
            inputs=self.model.inputs,
            outputs=[
                self.model.get_layer(self.last_conv_layer_name).output,
                self.model.output,
            ],
        )

        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_array)

            if pred_index is None:
                if predictions.shape[-1] == 1:
                    pred_index = 0
                else:
                    pred_index = tf.argmax(predictions[0])

            class_channel = predictions[:, pred_index]

        grads = tape.gradient(class_channel, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        heatmap = tf.maximum(heatmap, 0)

        max_value = tf.math.reduce_max(heatmap)
        if float(max_value.numpy()) == 0.0:
            return np.zeros(heatmap.shape, dtype=np.float32)

        heatmap = heatmap / max_value

        return np.asarray(heatmap.numpy(), dtype=np.float32)

    def _overlay_heatmap(self, image_array: np.ndarray, heatmap, alpha=0.5, gamma=2.0, percentile=80):
        heatmap = np.asarray(heatmap, dtype=np.float32)
        heatmap_resized = cv2.resize(
            heatmap,
            (image_array.shape[1], image_array.shape[0]),
            interpolation=cv2.INTER_LINEAR,
        )

        max_val = np.percentile(heatmap_resized, percentile)
        heatmap_resized = np.clip(heatmap_resized / (max_val + 1e-8), 0, 1)
        heatmap_resized = np.power(heatmap_resized, gamma)

        heatmap_u8 = np.uint8(255 * heatmap_resized)
        colored_heatmap = cv2.applyColorMap(heatmap_u8, cv2.COLORMAP_JET)
        colored_heatmap = cv2.cvtColor(colored_heatmap, cv2.COLOR_BGR2RGB)

        superimposed = (alpha * colored_heatmap) + ((1 - alpha) * image_array.astype(np.float32))
        superimposed = np.clip(superimposed, 0, 255).astype(np.uint8)

        return Image.fromarray(superimposed)

    def _find_last_conv_layer_name(self):
        for layer in reversed(self.model.layers):
            output_tensor = getattr(layer, "output", None)
            output_shape = getattr(output_tensor, "shape", None)
            if output_shape is not None and len(output_shape) == 4:
                return layer.name

        raise ValueError("Nenhuma camada convolucional 2D foi encontrada no modelo carregado.")
