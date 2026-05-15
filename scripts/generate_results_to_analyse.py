#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera figuras em results_to_analyse: imagem original (ou referência visual) | Grad-CAM + predições.

Apenas modelos binários (saída softmax com 2 classes). Combinações incoerentes são ignoradas
(ex.: modelo 3 canais com entrada apenas .npy sem conversão definida).
"""
import argparse
import csv
import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow.keras.applications.resnet50 import preprocess_input

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

os.chdir(project_root)

from pipelines.pre_processing_images import rgb_to_y_channel
from utils.gradcam import find_last_spatial_layer_name, make_gradcam_heatmap, overlay_jet_on_rgb


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}


def iter_val_raw(val_root: Path):
    if not val_root.is_dir():
        return
    for class_dir in sorted(val_root.iterdir()):
        if not class_dir.is_dir():
            continue
        label = class_dir.name
        for f in sorted(class_dir.iterdir()):
            if f.is_file() and f.suffix.lower() in IMAGE_EXTS:
                yield f, label


def iter_val_processed(val_root: Path):
    if not val_root.is_dir():
        return
    for class_dir in sorted(val_root.iterdir()):
        if not class_dir.is_dir():
            continue
        label = class_dir.name
        for f in sorted(class_dir.glob("*.npy")):
            yield f, label


def prepare_tensor_raw_rgb(pil_rgb: Image.Image):
    """224x224x3 + preprocess_input."""
    img = pil_rgb.convert("RGB").resize((224, 224))
    arr = np.expand_dims(np.asarray(img, dtype=np.float32), axis=0)
    arr = preprocess_input(arr.copy())
    disp = np.asarray(pil_rgb.resize((224, 224)), dtype=np.uint8)
    return tf.constant(arr, dtype=tf.float32), disp


def prepare_tensor_from_npy(npy_path: Path):
    """1-channel float tensor (1,224,224,1) as in training."""
    img = np.load(npy_path)
    if img.ndim == 2:
        img = img[..., np.newaxis]
    t = tf.constant(img[np.newaxis, ...], dtype=tf.float32)
    t = tf.image.resize(t, (224, 224))
    y = t.numpy()[0, ..., 0]
    disp = np.stack([y, y, y], axis=-1)
    disp = np.clip(disp * 255.0, 0, 255).astype(np.uint8)
    return tf.constant(t.numpy(), dtype=tf.float32), disp


def prepare_tensor_raw_for_1ch_model(pil_rgb: Image.Image):
    """Canal Y alinhado a batch_process_datasets (Otsu + bilateral)."""
    y = rgb_to_y_channel(pil_rgb.convert("RGB"), apply_otsu=True, apply_bilateral=True)
    y4 = y[..., np.newaxis].astype(np.float32)
    t = tf.image.resize(y4, (224, 224))
    t = t[tf.newaxis, ...]
    disp_rgb = np.asarray(pil_rgb.resize((224, 224)), dtype=np.uint8)
    return tf.constant(t.numpy(), dtype=tf.float32), disp_rgb


def run_one_image(model, tensor, display_rgb_uint8, last_conv_name, class_names):
    heatmap = make_gradcam_heatmap(tensor, model, last_conv_layer_name=last_conv_name)
    overlay = overlay_jet_on_rgb(display_rgb_uint8, heatmap)
    probs = model.predict(tensor, verbose=0)[0]
    pred_i = int(np.argmax(probs))
    title = (
        f"P({class_names[0]})={probs[0]:.3f}  P({class_names[1]})={probs[1]:.3f}  "
        f"→ {class_names[pred_i]}"
    )
    return overlay, title, probs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-images", type=int, default=None, help="Limite total de imagens (debug)")
    args = ap.parse_args()

    raw_val = project_root / "data" / "CO2Wounds-V2" / "raw" / "train_images_binary" / "val"
    proc_val = project_root / "data" / "CO2Wounds-V2" / "processed" / "train_images_binary" / "val"
    models_dir = project_root / "models"
    out_base = project_root / "results_to_analyse" / "figures"

    class_names = ["leprosy", "outros"]

    keras_paths = sorted(models_dir.glob("*.keras"))
    if not keras_paths:
        print("Nenhum arquivo .keras em models/.")
        return

    manifest_path = project_root / "results_to_analyse" / "predictions_manifest.csv"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    skipped_log = project_root / "results_to_analyse" / "skipped_pairs.log"

    total_counter = 0
    with open(manifest_path, "w", newline="", encoding="utf-8") as mf, open(
        skipped_log, "w", encoding="utf-8"
    ) as sk:
        w = csv.writer(mf)
        w.writerow(
            ["model", "val_split", "file", "true_folder", "p_leprosy", "p_outros", "pred", "conv_layer"]
        )

        for keras_path in keras_paths:
            try:
                model = tf.keras.models.load_model(keras_path, compile=False)
            except Exception as e:
                print(f"⚠️ Falha ao carregar {keras_path.name}: {e}")
                tf.keras.backend.clear_session()
                continue

            sh = model.output_shape
            n_out = sh[-1] if sh is not None else None
            if n_out != 2:
                print(f"⏭️ Ignorado (não binário): {keras_path.name} output={sh}")
                del model
                tf.keras.backend.clear_session()
                continue

            inch = model.input_shape[-1]
            last_conv = find_last_spatial_layer_name(model)
            print(f"\n▶ {keras_path.name}  in_ch={inch}  gradcam_layer={last_conv}")

            tasks = [
                ("raw_val", raw_val, "raw", iter_val_raw(raw_val)),
                ("processed_val", proc_val, "processed", iter_val_processed(proc_val)),
            ]

            done_all = False
            for split_name, val_root, kind, iterator in tasks:
                if done_all:
                    break
                if not val_root.is_dir():
                    sk.write(f"missing_dir\t{keras_path.name}\t{split_name}\t{val_root}\n")
                    print(f"  ⚠️ Pasta ausente: {val_root}")
                    continue

                for fpath, folder_label in iterator:
                    if args.max_images is not None and total_counter >= args.max_images:
                        done_all = True
                        break

                    skip_reason = None
                    tensor = disp = None

                    try:
                        if inch == 3:
                            if kind == "raw":
                                pil = Image.open(fpath)
                                tensor, disp = prepare_tensor_raw_rgb(pil)
                            else:
                                skip_reason = "model_3ch_npy_incompatible"
                        else:
                            if kind == "processed":
                                tensor, disp = prepare_tensor_from_npy(fpath)
                            else:
                                pil = Image.open(fpath)
                                tensor, disp = prepare_tensor_raw_for_1ch_model(pil)

                        if skip_reason:
                            sk.write(f"{skip_reason}\t{keras_path.stem}\t{split_name}\t{fpath}\n")
                            continue

                        overlay, title, probs = run_one_image(
                            model, tensor, disp, last_conv, class_names
                        )

                        rel = Path(folder_label) / f"{fpath.stem}.png"
                        dest = out_base / keras_path.stem / split_name / rel
                        dest.parent.mkdir(parents=True, exist_ok=True)

                        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
                        axes[0].imshow(disp)
                        axes[0].set_title("Entrada (referência)")
                        axes[0].axis("off")
                        axes[1].imshow(overlay)
                        axes[1].set_title("Grad-CAM")
                        axes[1].axis("off")
                        fig.suptitle(title, fontsize=10)
                        plt.tight_layout()
                        plt.savefig(dest, dpi=110, bbox_inches="tight")
                        plt.close(fig)

                        w.writerow(
                            [
                                keras_path.stem,
                                split_name,
                                str(fpath.relative_to(project_root)),
                                folder_label,
                                f"{probs[0]:.6f}",
                                f"{probs[1]:.6f}",
                                class_names[int(np.argmax(probs))],
                                last_conv,
                            ]
                        )
                        total_counter += 1
                    except Exception as e:
                        sk.write(f"error\t{keras_path.stem}\t{split_name}\t{fpath}\t{e}\n")
                        print(f"  ❌ {fpath}: {e}")

            del model
            tf.keras.backend.clear_session()

    print(f"\n✅ Concluído. Figuras em: {out_base}")
    print(f"✅ Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
