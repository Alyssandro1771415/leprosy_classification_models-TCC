# -*- coding: utf-8 -*-
"""Caminhos canônicos relativos à raiz do módulo ML (`ml/`)."""

from pathlib import Path

_ML_ROOT = Path(__file__).resolve().parents[2]


def get_ml_root() -> Path:
    return _ML_ROOT


def data_dir(*parts: str) -> Path:
    return _ML_ROOT / "data" / Path(*parts)


def artifacts_dir(*parts: str) -> Path:
    return _ML_ROOT / "artifacts" / Path(*parts)


def models_dir(dataset: str = "co2wounds") -> Path:
    path = artifacts_dir("models", dataset)
    path.mkdir(parents=True, exist_ok=True)
    return path


def metrics_dir() -> Path:
    path = artifacts_dir("metrics")
    path.mkdir(parents=True, exist_ok=True)
    return path


def figures_dir() -> Path:
    path = artifacts_dir("figures")
    path.mkdir(parents=True, exist_ok=True)
    return path


def training_plots_dir() -> Path:
    path = artifacts_dir("figures", "training_plots")
    path.mkdir(parents=True, exist_ok=True)
    return path
