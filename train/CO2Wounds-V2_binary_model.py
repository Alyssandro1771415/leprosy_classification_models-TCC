# -*- coding: utf-8 -*-
"""
Transfer learning (ResNet50 + ImageNet) for CO2Wounds-V2 binary classification.

--data raw: RGB folders under data/CO2Wounds-V2/raw/train_images_binary/
--data processed: .npy (canal Y) under data/CO2Wounds-V2/processed/train_images_binary/
  Must match pipelines/pre_processing_images.batch_process_datasets (Otsu + bilateral).
"""
import argparse
import json
import os
import pickle
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing.image import ImageDataGenerator

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.co2wounds_data import load_npy_dataset
from utils.models_to_pkl import save_model
from utils.tf_gpu import configure_gpu_memory_growth, log_gpu_status, require_gpu_or_exit
from utils.train_evaluation import (
    predict_generator_all_batches,
    predict_tf_dataset_all_batches,
    sklearn_binary_metrics_json,
)


def _dense_head(x):
    x = tf.keras.layers.Dense(1024, activation="relu")(x)
    x = tf.keras.layers.Dense(512, activation="relu")(x)
    x = tf.keras.layers.Dense(256, activation="relu")(x)
    x = tf.keras.layers.Dense(1024, activation="relu")(x)
    x = tf.keras.layers.Dense(512, activation="relu")(x)
    x = tf.keras.layers.Dense(256, activation="relu")(x)
    x = tf.keras.layers.Dense(1024, activation="relu")(x)
    x = tf.keras.layers.Dense(512, activation="relu")(x)
    x = tf.keras.layers.Dense(256, activation="relu")(x)
    x = tf.keras.layers.Dense(1024, activation="relu")(x)
    x = tf.keras.layers.Dense(512, activation="relu")(x)
    x = tf.keras.layers.Dense(256, activation="relu")(x)
    x = tf.keras.layers.Dense(1024, activation="relu")(x)
    x = tf.keras.layers.Dense(512, activation="relu")(x)
    x = tf.keras.layers.Dense(256, activation="relu")(x)
    x = tf.keras.layers.Dense(1024, activation="relu")(x)
    x = tf.keras.layers.Dense(512, activation="relu")(x)
    x = tf.keras.layers.Dense(256, activation="relu")(x)
    return tf.keras.layers.Dense(2, activation="softmax")(x)


def build_model_raw_transfer():
    pre_trained = tf.keras.applications.ResNet50(weights="imagenet", include_top=False)
    x = pre_trained.output
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    out = _dense_head(x)
    model = tf.keras.Model(inputs=pre_trained.input, outputs=out)
    for i, layer in enumerate(model.layers):
        layer.trainable = i >= 175
    return model


def build_model_processed_transfer():
    inp = tf.keras.layers.Input(shape=(224, 224, 1))
    ch = tf.keras.layers.Conv2D(3, (1, 1), padding="same", name="channel_expansion")(inp)
    base = tf.keras.applications.ResNet50(weights="imagenet", include_top=False, input_tensor=ch)
    x = base.output
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    out = _dense_head(x)
    model = tf.keras.Model(inputs=inp, outputs=out)
    unfreeze_from = max(0, len(base.layers) - 40)
    for i, layer in enumerate(base.layers):
        layer.trainable = i >= unfreeze_from
    model.get_layer("channel_expansion").trainable = True
    return model


def parse_args():
    p = argparse.ArgumentParser(description="CO2Wounds-V2 binary transfer learning")
    p.add_argument("--data", choices=["raw", "processed"], default="raw")
    p.add_argument("--require-gpu", action="store_true", help="Exit if no GPU is visible to TF")
    p.add_argument("--output-name", default=None, help="Base name for .keras and metrics files")
    p.add_argument("--epochs", type=int, default=30)
    p.add_argument("--batch-size", type=int, default=8)
    return p.parse_args()


def main():
    args = parse_args()
    os.chdir(project_root)

    configure_gpu_memory_growth()
    log_gpu_status()
    if args.require_gpu:
        require_gpu_or_exit()

    tf.keras.mixed_precision.set_global_policy("float32")

    if args.output_name:
        output_name = args.output_name
    else:
        output_name = (
            "modelo_binario_co2wounds_transfer_raw"
            if args.data == "raw"
            else "modelo_binario_co2wounds_transfer_processed"
        )

    raw_base = os.path.join(project_root, "data", "CO2Wounds-V2", "raw", "train_images_binary")
    proc_base = os.path.join(project_root, "data", "CO2Wounds-V2", "processed", "train_images_binary")

    metrics = [
        "accuracy",
        tf.keras.metrics.AUC(name="auc"),
        tf.keras.metrics.Precision(name="precision"),
        tf.keras.metrics.Recall(name="recall"),
    ]

    if args.data == "raw":
        modelo_binario = build_model_raw_transfer()

        train_datagen = ImageDataGenerator(
            preprocessing_function=preprocess_input,
            horizontal_flip=True,
            rotation_range=20,
            zoom_range=0.2,
        )
        val_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

        train_generator = train_datagen.flow_from_directory(
            os.path.join(raw_base, "train"),
            target_size=(224, 224),
            color_mode="rgb",
            batch_size=args.batch_size,
            class_mode="categorical",
            shuffle=True,
        )
        validation_generator = val_datagen.flow_from_directory(
            os.path.join(raw_base, "val"),
            target_size=(224, 224),
            color_mode="rgb",
            batch_size=args.batch_size,
            class_mode="categorical",
            shuffle=False,
        )

        modelo_binario.compile(optimizer="Adam", loss="categorical_crossentropy", metrics=metrics)

        reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.2, patience=3, min_lr=1e-6, verbose=1
        )
        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=5, restore_best_weights=True, verbose=1
        )

        history = modelo_binario.fit(
            train_generator,
            validation_data=validation_generator,
            epochs=args.epochs,
            callbacks=[reduce_lr, early_stopping],
        )

        y_true, y_prob = predict_generator_all_batches(modelo_binario, validation_generator)
        class_names = sorted(train_generator.class_indices.keys(), key=lambda k: train_generator.class_indices[k])

    else:
        modelo_binario = build_model_processed_transfer()

        datasets = {}
        for subset in ["train", "val", "test"]:
            subset_path = os.path.join(proc_base, subset)
            if os.path.exists(subset_path):
                X, y = load_npy_dataset(subset_path)
                datasets[subset] = (X, y)
                print(f"✅ {subset.upper()} carregado: {len(X)} imagens")
            else:
                print(f"❌ Pasta '{subset}' NÃO encontrada em {subset_path}")

        if "train" not in datasets or len(datasets["train"][0]) == 0:
            raise ValueError("Nenhum dado de treino .npy encontrado em processed/")

        X_train, y_train = datasets["train"]
        X_val, y_val = datasets.get("val", (None, None))
        if X_val is None or len(X_val) == 0:
            raise ValueError("Conjunto de validação .npy ausente ou vazio")

        y_train_ohe = tf.keras.utils.to_categorical(y_train, 2)
        y_val_ohe = tf.keras.utils.to_categorical(y_val, 2)

        def augment_image(x, y):
            x = tf.image.random_flip_left_right(x)
            return x, y

        train_dataset = (
            tf.data.Dataset.from_tensor_slices((X_train, y_train_ohe))
            .shuffle(1000)
            .map(augment_image, num_parallel_calls=tf.data.AUTOTUNE)
            .batch(args.batch_size)
            .prefetch(tf.data.AUTOTUNE)
        )
        val_dataset = tf.data.Dataset.from_tensor_slices((X_val, y_val_ohe)).batch(args.batch_size)

        modelo_binario.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
            loss="categorical_crossentropy",
            metrics=metrics,
        )

        reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.2, patience=3, min_lr=1e-6, verbose=1
        )
        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=5, restore_best_weights=True, verbose=1
        )

        history = modelo_binario.fit(
            train_dataset,
            validation_data=val_dataset,
            epochs=args.epochs,
            callbacks=[reduce_lr, early_stopping],
        )

        val_eval = tf.data.Dataset.from_tensor_slices((X_val, y_val_ohe)).batch(args.batch_size)
        y_true, y_prob = predict_tf_dataset_all_batches(modelo_binario, val_eval)
        class_names = ["leprosy", "outros"]

    save_model(modelo_binario, output_name)

    history_path = os.path.join(project_root, "models", f"{output_name}_history.pkl")
    with open(history_path, "wb") as f:
        pickle.dump(history.history, f)
    print(f"✅ Histórico salvo em: {history_path}")

    metrics_dir = os.path.join(project_root, "results_to_analyse", "metrics")
    sklearn_binary_metrics_json(
        y_true,
        y_prob,
        class_names,
        os.path.join(metrics_dir, f"{output_name}_val_sklearn.json"),
    )

    acc = history.history["accuracy"]
    val_acc = history.history["val_accuracy"]
    loss = history.history["loss"]
    val_loss = history.history["val_loss"]

    plot_dir = os.path.join(project_root, "results_to_analyse", "training_plots")
    os.makedirs(plot_dir, exist_ok=True)
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(acc, label="Treino")
    plt.plot(val_acc, label="Validação")
    plt.xlabel("Épocas")
    plt.ylabel("Acurácia")
    plt.legend()
    plt.title("Acurácia")
    plt.subplot(1, 2, 2)
    plt.plot(loss, label="Treino")
    plt.plot(val_loss, label="Validação")
    plt.xlabel("Épocas")
    plt.ylabel("Loss")
    plt.legend()
    plt.title("Loss")
    plt.tight_layout()
    plot_path = os.path.join(plot_dir, f"{output_name}_curves.png")
    plt.savefig(plot_path, dpi=120)
    plt.close()
    print(f"✅ Curvas salvas em: {plot_path}")

    info = {
        "class_names": list(class_names),
        "data_mode": args.data,
        "output_name": output_name,
        "final_train_acc": float(acc[-1]),
        "final_val_acc": float(val_acc[-1]),
    }
    with open(os.path.join(metrics_dir, f"{output_name}_summary.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)

    print(f"\n📊 Resumo: épocas={len(acc)} train_acc={acc[-1]:.4f} val_acc={val_acc[-1]:.4f}")


if __name__ == "__main__":
    main()
