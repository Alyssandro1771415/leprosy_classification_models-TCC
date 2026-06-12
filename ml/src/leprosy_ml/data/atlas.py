# -*- coding: utf-8 -*-
"""Split estratificado 70/20/10 (treino/validação/teste) para datasets Atlas Dermatology."""

import glob
import os

import numpy as np
import pandas as pd

ATLAS_TRAIN_RATIO = 0.7
ATLAS_VAL_RATIO = 0.2
ATLAS_TEST_RATIO = 0.1
ATLAS_SPLIT_SEED = 42

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG")


def stratified_train_val_test_split(
    X,
    y,
    train_ratio=ATLAS_TRAIN_RATIO,
    val_ratio=ATLAS_VAL_RATIO,
    test_ratio=ATLAS_TEST_RATIO,
    random_state=ATLAS_SPLIT_SEED,
):
    """Divide arrays em treino, validação e teste mantendo proporção por classe."""
    total = train_ratio + val_ratio + test_ratio
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"As proporções devem somar 1.0 (recebido {total})")

    rng = np.random.RandomState(random_state)
    train_indices, val_indices, test_indices = [], [], []

    for class_label in np.unique(y):
        class_indices = np.where(y == class_label)[0]
        rng.shuffle(class_indices)

        n = len(class_indices)
        n_test = int(n * test_ratio)
        n_val = int(n * val_ratio)

        test_indices.extend(class_indices[:n_test])
        val_indices.extend(class_indices[n_test : n_test + n_val])
        train_indices.extend(class_indices[n_test + n_val :])

    for indices in (train_indices, val_indices, test_indices):
        rng.shuffle(indices)

    return (
        X[train_indices],
        X[val_indices],
        X[test_indices],
        y[train_indices],
        y[val_indices],
        y[test_indices],
    )


def collect_image_paths(data_dir):
    """Lista caminhos absolutos de imagens agrupados por subpasta (classe)."""
    rows = []
    for class_name in sorted(os.listdir(data_dir)):
        class_dir = os.path.join(data_dir, class_name)
        if not os.path.isdir(class_dir):
            continue
        for path in sorted(glob.glob(os.path.join(class_dir, "*"))):
            if path.lower().endswith(IMAGE_EXTENSIONS):
                rows.append({"filename": path, "class": class_name})
    return rows


def stratified_split_dataframes(
    data_dir,
    train_ratio=ATLAS_TRAIN_RATIO,
    val_ratio=ATLAS_VAL_RATIO,
    test_ratio=ATLAS_TEST_RATIO,
    random_state=ATLAS_SPLIT_SEED,
):
    """Retorna DataFrames de treino, validação e teste a partir de um diretório por classe."""
    rows = collect_image_paths(data_dir)
    if not rows:
        raise ValueError(f"Nenhuma imagem encontrada em {data_dir}")

    rng = np.random.RandomState(random_state)
    train_rows, val_rows, test_rows = [], [], []

    df = pd.DataFrame(rows)
    for class_name, group in df.groupby("class"):
        indices = group.index.to_numpy()
        rng.shuffle(indices)

        n = len(indices)
        n_test = int(n * test_ratio)
        n_val = int(n * val_ratio)

        test_rows.extend(group.loc[indices[:n_test]].to_dict("records"))
        val_rows.extend(group.loc[indices[n_test : n_test + n_val]].to_dict("records"))
        train_rows.extend(group.loc[indices[n_test + n_val :]].to_dict("records"))

    return (
        pd.DataFrame(train_rows).sample(frac=1, random_state=random_state).reset_index(drop=True),
        pd.DataFrame(val_rows).sample(frac=1, random_state=random_state + 1).reset_index(drop=True),
        pd.DataFrame(test_rows).sample(frac=1, random_state=random_state + 2).reset_index(drop=True),
    )
