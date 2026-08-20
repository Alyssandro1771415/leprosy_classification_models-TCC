# -*- coding: utf-8 -*-
"""
ResNet50 from scratch (no ImageNet weights) for CO2Wounds-V2 binary classification.

--data raw: RGB under data/CO2Wounds-V2/raw/train_images_binary/ (ResNet input 224x224x3).
--data processed: .npy canal Y under data/CO2Wounds-V2/processed/train_images_binary/
  (input 224x224x1 + channel_expansion). Align .npy with pipelines/pre_processing_images
  batch_process_datasets (Otsu + bilateral).
"""
import argparse
import json
import os
import pickle

# Antes de importar TensorFlow: evita JIT XLA (estoura VRAM / falha em GPUs antigas)
os.environ.setdefault("TF_XLA_FLAGS", "--tf_xla_auto_jit=0")
os.environ.setdefault("TF_FORCE_GPU_ALLOW_GROWTH", "true")

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
from leprosy_ml.preprocessing.ablation import ABLATION_VARIANTS, variant_processed_dir
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

    A versão anterior empilhava 18 camadas Dense (7,4M params) sem normalização nem
    dropout: o gradiente se dissolvia na pilha e o treino estacionava no mínimo local
    de prever sempre a classe majoritária.
    """
    x = tf.keras.layers.Dense(256, use_bias=False)(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Activation("relu")(x)
    x = tf.keras.layers.Dropout(dropout)(x)
    x = tf.keras.layers.Dense(128, use_bias=False)(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Activation("relu")(x)
    x = tf.keras.layers.Dropout(dropout / 2)(x)
    return tf.keras.layers.Dense(2, activation="softmax", dtype="float32")(x)


def build_model_processed_from_zero(dropout=0.5):
    input_layer = tf.keras.layers.Input(shape=(224, 224, 1))
    x = tf.keras.layers.Conv2D(3, (1, 1), padding="same", name="channel_expansion")(input_layer)
    base_model = tf.keras.applications.ResNet50(weights=None, include_top=False, input_tensor=x)
    x = base_model.output
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    out = _dense_head(x, dropout=dropout)
    model = tf.keras.Model(inputs=input_layer, outputs=out)
    for layer in model.layers:
        layer.trainable = True
    return model


def build_model_raw_from_zero(dropout=0.5):
    inp = tf.keras.layers.Input(shape=(224, 224, 3))
    base_model = tf.keras.applications.ResNet50(weights=None, include_top=False, input_tensor=inp)
    x = base_model.output
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    out = _dense_head(x, dropout=dropout)
    model = tf.keras.Model(inputs=inp, outputs=out)
    for layer in model.layers:
        layer.trainable = True
    return model


def parse_args():
    p = argparse.ArgumentParser(description="CO2Wounds-V2 binary ResNet50 from zero")
    p.add_argument("--data", choices=["raw", "processed"], default="processed")
    p.add_argument(
        "--processed-variant",
        choices=[v.name for v in ABLATION_VARIANTS],
        default=None,
        help="Variante de pré-processamento (processed/ablation/{variant}/)",
    )
    p.add_argument("--require-gpu", action="store_true")
    p.add_argument("--output-name", default=None)
    p.add_argument("--epochs", type=int, default=40)
    # Batch pequeno demais quebra as BatchNorm do ResNet50 (estatísticas de 1 amostra).
    # Se estourar VRAM (RESOURCE_EXHAUSTED), caia para 8 — nunca para 1.
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument(
        "--no-class-weight",
        action="store_true",
        help="Desliga o peso maior na classe minoritária (padrão: ligado)",
    )
    p.add_argument("--dropout", type=float, default=0.5, help="Dropout da cabeça densa")
    p.add_argument("--learning-rate", type=float, default=1e-4)
    p.add_argument(
        "--mixed-precision",
        action="store_true",
        default=True,
        help="Usar mixed_float16 (padrão: ligado; reduz VRAM)",
    )
    p.add_argument(
        "--no-mixed-precision",
        action="store_true",
        help="Desliga mixed_float16",
    )
    return p.parse_args()


def main():
    args = parse_args()
    os.chdir(ml_root)

    configure_gpu_memory_growth()
    try:
        tf.config.optimizer.set_jit(False)
    except Exception:
        pass
    log_gpu_status()
    if args.require_gpu:
        require_gpu_or_exit()

    use_mixed = args.mixed_precision and not args.no_mixed_precision
    if use_mixed:
        tf.keras.mixed_precision.set_global_policy("mixed_float16")
        print("mixed_precision: mixed_float16")
    else:
        tf.keras.mixed_precision.set_global_policy("float32")
        print("mixed_precision: float32")

    print(f"batch_size={args.batch_size}")

    if args.output_name:
        output_name = args.output_name
    elif args.data == "raw":
        output_name = "modelo_binario_co2wounds_fromzero_raw"
    elif args.processed_variant:
        output_name = f"modelo_binario_co2wounds_ablation_{args.processed_variant}"
    else:
        output_name = "modelo_binario_co2wounds_fromzero_processed"

    raw_base = data_dir("co2wounds_v2", "raw", "train_images_binary")
    if args.data == "processed" and args.processed_variant:
        proc_base = variant_processed_dir(args.processed_variant)
    else:
        proc_base = data_dir("co2wounds_v2", "processed", "train_images_binary")

    metrics = [
        "accuracy",
        tf.keras.metrics.AUC(name="auc"),
        tf.keras.metrics.Precision(name="precision"),
        tf.keras.metrics.Recall(name="recall"),
    ]

    class_names_default = ["leprosy", "outros"]
    co2wounds_models = models_dir("co2wounds")

    def build_callbacks():
        """
        Monitora `val_auc` em vez de `val_loss`: com classes desbalanceadas, a AUC
        acusa ganho de ranqueamento mesmo enquanto a acurácia está presa no baseline
        da classe majoritária — e é isso que separa "aprendendo devagar" de "colapsou".
        """
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
        modelo_binario = build_model_raw_from_zero(dropout=args.dropout)

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
        n_train = train_generator.samples
        n_val = validation_generator.samples
        train_class_counts = {
            name: counts_by_index[idx] for name, idx in train_generator.class_indices.items()
        }

    else:
        modelo_binario = build_model_processed_from_zero(dropout=args.dropout)

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
            raise ValueError("Nenhum dado de treino encontrado!")

        X_train, y_train = datasets["train"]
        X_val, y_val = datasets.get("val", (None, None))
        X_test, y_test = datasets.get("test", (None, None))
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

        counts_by_index = {
            idx: int((np.asarray(y_train) == idx).sum()) for idx in range(len(class_names_default))
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
        class_names = class_names_default
        n_train = len(X_train)
        n_val = len(X_val)
        train_class_counts = {
            name: counts_by_index[idx] for idx, name in enumerate(class_names)
        }

    save_model(modelo_binario, output_name, dataset="co2wounds")

    history_path = co2wounds_models / f"{output_name}_history.pkl"
    with open(history_path, "wb") as f:
        pickle.dump(history.history, f)
    print(f"✅ Histórico salvo em: {history_path}")

    n_test = 0
    if args.data == "processed" and "test" in datasets and len(datasets["test"][0]) > 0:
        n_test = len(datasets["test"][0])

    dataset_info = {
        "class_names": ["leprosy", "outros"],
        "train_images": int(n_train),
        "val_images": int(n_val),
        "test_images": int(n_test),
        "num_classes": 2,
        "data_mode": args.data,
        "processed_variant": args.processed_variant,
        "processed_dir": str(proc_base) if args.data == "processed" else None,
        "input_shape": tuple(int(x) for x in modelo_binario.input_shape[1:]),
        "total_images": int(n_train + n_val + n_test),
        "class_distribution": train_class_counts,
    }
    info_path = co2wounds_models / f"{output_name}_info.pkl"
    with open(info_path, "wb") as f:
        pickle.dump(dataset_info, f)

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

    with open(out_metrics / f"{output_name}_summary.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "class_names": list(class_names),
                "data_mode": args.data,
                "processed_variant": args.processed_variant,
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
            },
            f,
            indent=2,
        )

    gap = acc[-1] - val_acc[-1]
    print(f"\n📊 Resumo: épocas={len(acc)} train_acc={acc[-1]:.4f} val_acc={val_acc[-1]:.4f} gap={gap:.4f}")


if __name__ == "__main__":
    main()
