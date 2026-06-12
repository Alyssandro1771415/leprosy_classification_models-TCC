# -*- coding: utf-8 -*-
"""Load CO2Wounds-V2 binary .npy splits (leprosy / outros) for training."""

import glob
import os

import numpy as np
import tensorflow as tf


def load_npy_dataset(data_dir, target_size=(224, 224)):
    images = []
    labels = []
    class_names = ["leprosy", "outros"]
    class_to_idx = {name: idx for idx, name in enumerate(class_names)}

    print(f"\n🔍 Carregando dados de: {os.path.abspath(data_dir)}")
    for class_name in class_names:
        class_dir = os.path.join(data_dir, class_name)
        if not os.path.exists(class_dir):
            print(f"⚠️ Diretório não encontrado: {class_dir}")
            continue

        npy_files = glob.glob(os.path.join(class_dir, "*.npy"))
        print(f"  -> {class_name}: {len(npy_files)} arquivos")

        for npy_file in npy_files:
            try:
                img = np.load(npy_file)
                if img.shape != target_size:
                    img = tf.image.resize(img[..., np.newaxis], target_size).numpy()
                else:
                    img = img[..., np.newaxis]
                images.append(img)
                labels.append(class_to_idx[class_name])
            except Exception as e:
                print(f"❌ Erro ao processar {npy_file}: {e}")

    return np.array(images), np.array(labels)
