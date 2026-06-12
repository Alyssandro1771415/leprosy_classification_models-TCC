# -*- coding: utf-8 -*-
"""Grad-CAM helpers: last spatial layer discovery and heatmap generation."""

import numpy as np
import tensorflow as tf


def find_last_spatial_layer_name(model):
    """Name of the last layer whose output rank is 4 (B, H, W, C)."""
    for layer in reversed(model.layers):
        out = getattr(layer, "output", None)
        shape = getattr(out, "shape", None) if out is not None else None
        if shape is not None and len(shape) == 4:
            return layer.name
    raise ValueError("Nenhuma camada com mapa espacial (rank 4) encontrada no modelo.")


def make_gradcam_heatmap(img_array, model, last_conv_layer_name=None, pred_index=None):
    """
    img_array: batch (1, H, W, C) float tensor ready for model.predict (already preprocessed).
    """
    if last_conv_layer_name is None:
        last_conv_layer_name = find_last_spatial_layer_name(model)

    conv_layer = model.get_layer(last_conv_layer_name)
    grad_model = tf.keras.models.Model(
        [model.inputs], [conv_layer.output, model.output]
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        if pred_index is None:
            pred_index = int(tf.argmax(predictions[0]).numpy())
        class_channel = predictions[:, pred_index]

    grads = tape.gradient(class_channel, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0.0)

    max_value = tf.math.reduce_max(heatmap)
    if float(max_value.numpy()) == 0.0:
        return np.zeros(heatmap.shape, dtype=np.float32)

    heatmap = heatmap / max_value
    return heatmap.numpy()


def overlay_jet_on_rgb(rgb_uint8, heatmap, alpha=0.5, gamma=2.0, percentile=80):
    """
    rgb_uint8: (H, W, 3) uint8
    heatmap: (h, w) float 0..1, will be resized to rgb shape
    """
    import cv2

    h0, w0 = rgb_uint8.shape[:2]
    hm = cv2.resize(heatmap, (w0, h0), interpolation=cv2.INTER_LINEAR)
    max_val = float(np.percentile(hm, percentile))
    hm = np.clip(hm / (max_val + 1e-8), 0.0, 1.0)
    hm = np.power(hm, gamma)
    hm_u8 = np.uint8(255 * hm)
    hm_color = cv2.applyColorMap(hm_u8, cv2.COLORMAP_JET)
    hm_color = cv2.cvtColor(hm_color, cv2.COLOR_BGR2RGB)
    base = rgb_uint8.astype(np.float32)
    out = alpha * hm_color + (1.0 - alpha) * base
    return np.clip(out, 0, 255).astype(np.uint8)
