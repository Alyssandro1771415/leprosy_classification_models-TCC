# -*- coding: utf-8 -*-
"""TensorFlow GPU visibility and optional hard requirement for training scripts."""

import sys

import tensorflow as tf


def configure_gpu_memory_growth():
    gpus = tf.config.experimental.list_physical_devices("GPU")
    for gpu in gpus:
        try:
            tf.config.experimental.set_memory_growth(gpu, True)
        except RuntimeError:
            pass
    return gpus


def log_gpu_status():
    gpus = tf.config.list_physical_devices("GPU")
    print(f"\n{'='*60}")
    print("TensorFlow devices")
    print(f"  GPU count: {len(gpus)}")
    for i, device in enumerate(gpus):
        print(f"  [{i}] {device.name}")
    cpus = tf.config.list_physical_devices("CPU")
    print(f"  CPU count: {len(cpus)}")
    _ = tf.constant(0.0)
    print(f"{'='*60}\n")
    return gpus


def require_gpu_or_exit():
    gpus = tf.config.list_physical_devices("GPU")
    if not gpus:
        print(
            "ERROR: --require-gpu was set but no GPU was found. "
            "Check CUDA/cuDNN and NVIDIA drivers.",
            file=sys.stderr,
        )
        sys.exit(1)
    return gpus
