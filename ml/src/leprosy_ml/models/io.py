# -*- coding: utf-8 -*-
"""Salvamento e carregamento de checkpoints Keras (.keras)."""

from pathlib import Path

import tensorflow as tf

from leprosy_ml.paths import get_ml_root, models_dir


def _resolve_model_path(model_name: str, dataset: str = "co2wounds") -> Path:
    name = model_name.removesuffix(".keras")
    candidate = models_dir(dataset) / f"{name}.keras"
    if candidate.is_file():
        return candidate

    legacy = get_ml_root().parent / "models" / f"{name}.keras"
    if legacy.is_file():
        return legacy

    flat = models_dir(dataset).parent.parent / "models" / f"{name}.keras"
    if flat.is_file():
        return flat

    return candidate


def save_model(model_to_save, model_name: str, dataset: str = "co2wounds") -> Path:
    """Salva um modelo Keras no formato oficial (.keras)."""
    out_dir = models_dir(dataset)
    model_path = out_dir / f"{model_name}.keras"
    model_to_save.save(str(model_path))
    print(f"✅ Modelo salvo em: {model_path}")
    return model_path


def load_model(model_name: str, dataset: str = "co2wounds"):
    """Carrega um modelo Keras salvo (nome sem extensão ou caminho completo)."""
    path = Path(model_name)
    if path.suffix == ".keras" and path.is_file():
        model_path = path
    else:
        model_path = _resolve_model_path(str(model_name), dataset=dataset)

    model = tf.keras.models.load_model(str(model_path))
    print(f"✅ Modelo carregado de: {model_path}")
    return model
