# -*- coding: utf-8 -*-
"""Amostras de validação (leprosy + outros) para notebooks de visualização."""

import os
from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np

CLASS_NAMES = ("leprosy", "outros")
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def predicted_class(probs) -> str:
    """Classe prevista a partir da saída do modelo (índice 0=leprosy, 1=outros)."""
    probs = np.asarray(probs).ravel()
    if len(probs) == 2:
        return CLASS_NAMES[int(np.argmax(probs))]
    if len(probs) == 1:
        return CLASS_NAMES[0] if probs[0] >= 0.5 else CLASS_NAMES[1]
    return CLASS_NAMES[int(np.argmax(probs))]


def format_probs_percent(probs) -> str:
    probs = np.asarray(probs).ravel()
    if len(probs) == 2:
        return f"leprosy {probs[0] * 100:.2f}% | outros {probs[1] * 100:.2f}%"
    if len(probs) == 1:
        return f"saída única {probs[0] * 100:.2f}%"
    parts = [f"classe {i} {p * 100:.2f}%" for i, p in enumerate(probs)]
    return " | ".join(parts)


def shuffle_samples(samples: Sequence, seed: Optional[int] = 42) -> List:
    out = list(samples)
    rng = np.random.default_rng(seed)
    rng.shuffle(out)
    return out


def list_val_rgb_images(val_root: str) -> List[Tuple[str, str, str]]:
    """(stem, caminho_jpg, classe_real) em val/leprosy e val/outros."""
    samples = []
    for class_name in CLASS_NAMES:
        class_dir = os.path.join(val_root, class_name)
        if not os.path.isdir(class_dir):
            continue
        for name in os.listdir(class_dir):
            if not name.lower().endswith(IMAGE_EXTENSIONS):
                continue
            stem = os.path.splitext(name)[0]
            samples.append((stem, os.path.join(class_dir, name), class_name))
    return samples


def list_val_npy_images(val_root: str) -> List[Tuple[str, str, str]]:
    """(stem, caminho_npy, classe_real) em val/leprosy e val/outros."""
    samples = []
    for class_name in CLASS_NAMES:
        class_dir = os.path.join(val_root, class_name)
        if not os.path.isdir(class_dir):
            continue
        for name in os.listdir(class_dir):
            if not name.endswith(".npy"):
                continue
            stem = os.path.splitext(name)[0]
            samples.append((stem, os.path.join(class_dir, name), class_name))
    return samples


def list_val_paired_images(raw_val_root: str, npy_val_root: str) -> List[Tuple[str, str, str, str]]:
    """(stem, jpg, npy, classe_real) com par raw+npy na mesma subpasta de val."""
    samples = []
    for class_name in CLASS_NAMES:
        raw_class = os.path.join(raw_val_root, class_name)
        npy_class = os.path.join(npy_val_root, class_name)
        if not os.path.isdir(raw_class) or not os.path.isdir(npy_class):
            continue

        raw_by_stem = {}
        for name in os.listdir(raw_class):
            if not name.lower().endswith(IMAGE_EXTENSIONS):
                continue
            stem = os.path.splitext(name)[0]
            raw_by_stem[stem] = os.path.join(raw_class, name)

        for name in os.listdir(npy_class):
            if not name.endswith(".npy"):
                continue
            stem = os.path.splitext(name)[0]
            jpg_path = raw_by_stem.get(stem)
            if jpg_path is None:
                continue
            samples.append((stem, jpg_path, os.path.join(npy_class, name), class_name))
    return samples
