import base64
import io

import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow.keras.applications.resnet50 import preprocess_input


class ModelFocusService:
    def __init__(self, model):
        self.model = model
        self.last_conv_layer_name = self._find_last_conv_layer_name()

    def generate_focus_base64(self, image_bytes: bytes) -> str:
        original_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_array = self._prepare_image_array(original_image)
        heatmap = self._make_gradcam_heatmap(img_array)
        focused_image = self._overlay_heatmap(original_image, heatmap)

        buffer = io.BytesIO()
        focused_image.save(buffer, format="PNG")

        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def _prepare_image_array(self, image: Image.Image):
        resized_image = image.resize((224, 224))
        img_array = np.array(resized_image, dtype=np.float32)
        img_array = np.expand_dims(img_array, axis=0)

        return preprocess_input(img_array)

    def _make_gradcam_heatmap(self, img_array, pred_index=None):
        grad_model = tf.keras.models.Model(
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

        return heatmap.numpy()

    def _overlay_heatmap(self, image: Image.Image, heatmap, alpha=0.5, gamma=2.0, percentile=80):
        image_array = np.array(image, dtype=np.float32)

        heatmap_image = Image.fromarray(np.uint8(heatmap * 255))
        heatmap_image = heatmap_image.resize(image.size, Image.Resampling.BILINEAR)
        heatmap_resized = np.array(heatmap_image, dtype=np.float32) / 255.0

        max_val = np.percentile(heatmap_resized, percentile)
        heatmap_resized = np.clip(heatmap_resized / (max_val + 1e-8), 0, 1)
        heatmap_resized = np.power(heatmap_resized, gamma)

        colored_heatmap = self._apply_jet_colormap(heatmap_resized)
        superimposed = (alpha * colored_heatmap) + ((1 - alpha) * image_array)
        superimposed = np.clip(superimposed, 0, 255).astype(np.uint8)

        return Image.fromarray(superimposed)

    def _apply_jet_colormap(self, heatmap):
        red = np.clip(1.5 - np.abs((4 * heatmap) - 3), 0, 1)
        green = np.clip(1.5 - np.abs((4 * heatmap) - 2), 0, 1)
        blue = np.clip(1.5 - np.abs((4 * heatmap) - 1), 0, 1)

        return np.stack([red, green, blue], axis=-1) * 255.0

    def _find_last_conv_layer_name(self):
        for layer in reversed(self.model.layers):
            output_tensor = getattr(layer, "output", None)
            output_shape = getattr(output_tensor, "shape", None)
            if output_shape is not None and len(output_shape) == 4:
                return layer.name

        raise ValueError("Nenhuma camada convolucional 2D foi encontrada no modelo carregado.")
