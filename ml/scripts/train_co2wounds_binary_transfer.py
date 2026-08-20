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

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from leprosy_ml.data.co2wounds import load_npy_dataset
from leprosy_ml.models.io import save_model
from leprosy_ml.paths import data_dir, get_ml_root, metrics_dir, models_dir, training_plots_dir
from leprosy_ml.training.gpu import configure_gpu_memory_growth, log_gpu_status, require_gpu_or_exit
from leprosy_ml.training.weights import balanced_class_weights
from leprosy_ml.evaluation.metrics import (
    overfitting_report,
    predict_generator_all_batches,
    predict_tf_dataset_all_batches,
    sklearn_binary_metrics_json,
)

ml_root = get_ml_root()


def _dense_head(x, dropout=0.5):
    """
    Cabeça compacta com normalização e dropout.

    A versão anterior empilhava 18 camadas Dense sem normalização nem dropout, o que
    fazia o treino estacionar em prever sempre a classe majoritária.
    """
    x = tf.keras.layers.Dense(256, use_bias=False)(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Activation("relu")(x)
    x = tf.keras.layers.Dropout(dropout)(x)
    x = tf.keras.layers.Dense(128, use_bias=False)(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Activation("relu")(x)
    x = tf.keras.layers.Dropout(dropout / 2)(x)
    return tf.keras.layers.Dense(2, activation="softmax")(x)


def build_model_raw_transfer(dropout=0.5):
    pre_trained = tf.keras.applications.ResNet50(weights="imagenet", include_top=False)
    x = pre_trained.output
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    out = _dense_head(x, dropout=dropout)
    model = tf.keras.Model(inputs=pre_trained.input, outputs=out)
    for i, layer in enumerate(model.layers):
        layer.trainable = i >= 175
    return model


def build_model_processed_transfer(dropout=0.5):
    inp = tf.keras.layers.Input(shape=(224, 224, 1))
    ch = tf.keras.layers.Conv2D(3, (1, 1), padding="same", name="channel_expansion")(inp)
    base = tf.keras.applications.ResNet50(weights="imagenet", include_top=False, input_tensor=ch)
    x = base.output
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    out = _dense_head(x, dropout=dropout)
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
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument(
        "--no-class-weight",
        action="store_true",
        help="Desliga o peso maior na classe minoritária (padrão: ligado)",
    )
    p.add_argument("--dropout", type=float, default=0.5, help="Dropout da cabeça densa")
    p.add_argument("--learning-rate", type=float, default=1e-4)
    return p.parse_args()


def main():
    args = parse_args()
    os.chdir(ml_root)

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

    raw_base = data_dir("co2wounds_v2", "raw", "train_images_binary")
    proc_base = data_dir("co2wounds_v2", "processed", "train_images_binary")

    metrics = [
        "accuracy",
        tf.keras.metrics.AUC(name="auc"),
        tf.keras.metrics.Precision(name="precision"),
        tf.keras.metrics.Recall(name="recall"),
    ]

    def build_callbacks():
        """Monitora `val_auc`: com classes desbalanceadas, acusa ganho real de
        ranqueamento mesmo com a acurácia presa no baseline da classe majoritária."""
        return [
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor="val_auc", mode="max", factor=0.2, patience=4, min_lr=1e-6, verbose=1
            ),
            tf.keras.callbacks.EarlyStopping(
                monitor="val_auc",
                mode="max",
                patience=8,
                min_delta=1e-3,
                restore_best_weights=True,
                verbose=1,
            ),
        ]

    if args.data == "raw":
        modelo_binario = build_model_raw_transfer(dropout=args.dropout)

        train_datagen = ImageDataGenerator(
            preprocessing_function=preprocess_input,
            horizontal_flip=True,
            rotation_range=20,
            zoom_range=0.2,
        )
        val_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

        train_generator = train_datagen.flow_from_directory(
            str(raw_base / "train"),
            target_size=(224, 224),
            color_mode="rgb",
            batch_size=args.batch_size,
            class_mode="categorical",
            shuffle=True,
        )
        validation_generator = val_datagen.flow_from_directory(
            str(raw_base / "val"),
            target_size=(224, 224),
            color_mode="rgb",
            batch_size=args.batch_size,
            class_mode="categorical",
            shuffle=False,
        )

        modelo_binario.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=args.learning_rate),
            loss="categorical_crossentropy",
            metrics=metrics,
        )

        counts_by_index = {
            idx: int((np.asarray(train_generator.classes) == idx).sum())
            for idx in train_generator.class_indices.values()
        }
        class_weight = None if args.no_class_weight else balanced_class_weights(counts_by_index)
        print(f"class_weight: {class_weight}")

        history = modelo_binario.fit(
            train_generator,
            validation_data=validation_generator,
            epochs=args.epochs,
            callbacks=build_callbacks(),
            class_weight=class_weight,
        )

        y_true, y_prob = predict_generator_all_batches(modelo_binario, validation_generator)
        class_names = sorted(train_generator.class_indices.keys(), key=lambda k: train_generator.class_indices[k])
        train_class_counts = {
            name: counts_by_index[idx] for name, idx in train_generator.class_indices.items()
        }

    else:
        modelo_binario = build_model_processed_transfer(dropout=args.dropout)

        datasets = {}
        for subset in ["train", "val", "test"]:
            subset_path = proc_base / subset
            if subset_path.exists():
                X, y = load_npy_dataset(str(subset_path))
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

        # drop_remainder evita um último batch minúsculo, que desestabiliza as BatchNorm
        train_dataset = (
            tf.data.Dataset.from_tensor_slices((X_train, y_train_ohe))
            .shuffle(len(X_train), reshuffle_each_iteration=True)
            .map(augment_image, num_parallel_calls=tf.data.AUTOTUNE)
            .batch(args.batch_size, drop_remainder=True)
            .prefetch(tf.data.AUTOTUNE)
        )
        val_dataset = tf.data.Dataset.from_tensor_slices((X_val, y_val_ohe)).batch(args.batch_size)

        modelo_binario.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=args.learning_rate),
            loss="categorical_crossentropy",
            metrics=metrics,
        )

        class_names = ["leprosy", "outros"]
        counts_by_index = {
            idx: int((np.asarray(y_train) == idx).sum()) for idx in range(len(class_names))
        }
        class_weight = None if args.no_class_weight else balanced_class_weights(counts_by_index)
        print(f"class_weight: {class_weight}")

        history = modelo_binario.fit(
            train_dataset,
            validation_data=val_dataset,
            epochs=args.epochs,
            callbacks=build_callbacks(),
            class_weight=class_weight,
        )

        val_eval = tf.data.Dataset.from_tensor_slices((X_val, y_val_ohe)).batch(args.batch_size)
        y_true, y_prob = predict_tf_dataset_all_batches(modelo_binario, val_eval)
        train_class_counts = {name: counts_by_index[idx] for idx, name in enumerate(class_names)}

    save_model(modelo_binario, output_name, dataset="co2wounds")

    history_path = models_dir("co2wounds") / f"{output_name}_history.pkl"
    with open(history_path, "wb") as f:
        pickle.dump(history.history, f)
    print(f"✅ Histórico salvo em: {history_path}")

    out_metrics = metrics_dir()
    sklearn_binary_metrics_json(
        y_true,
        y_prob,
        class_names,
        out_metrics / f"{output_name}_val_sklearn.json",
    )

    acc = history.history["accuracy"]
    val_acc = history.history["val_accuracy"]
    loss = history.history["loss"]
    val_loss = history.history["val_loss"]

    plot_dir = training_plots_dir()
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
    plot_path = plot_dir / f"{output_name}_curves.png"
    plt.savefig(plot_path, dpi=120)
    plt.close()
    print(f"✅ Curvas salvas em: {plot_path}")

    diagnosis = overfitting_report(
        history,
        out_metrics / f"{output_name}_overfitting.json",
        class_counts=train_class_counts,
    )

    info = {
        "class_names": list(class_names),
        "data_mode": args.data,
        "output_name": output_name,
        "final_train_acc": float(acc[-1]),
        "final_val_acc": float(val_acc[-1]),
        "train_class_counts": train_class_counts,
        "overfitting": diagnosis["veredito"],
        "overfitting_gap": diagnosis["gap_acuracia"],
        "hiperparametros": {
            "batch_size": args.batch_size,
            "learning_rate": args.learning_rate,
            "dropout": args.dropout,
            "class_weight": class_weight,
            "monitor": "val_auc",
        },
    }
    with open(out_metrics / f"{output_name}_summary.json", "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)

    print(
        f"\n📊 Resumo: épocas={len(acc)} train_acc={acc[-1]:.4f} val_acc={val_acc[-1]:.4f} "
        f"gap={acc[-1] - val_acc[-1]:.4f}"
    )


if __name__ == "__main__":
    main()
