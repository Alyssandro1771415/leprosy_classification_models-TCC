# -*- coding: utf-8 -*-
"""Post-training binary classification metrics (sklearn + JSON export)."""

import json
from pathlib import Path

import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score


def sklearn_binary_metrics_json(
    y_true_int,
    y_pred_probs,
    class_names,
    out_path,
):
    """
    y_true_int: (N,) integers 0..1
    y_pred_probs: (N, 2) softmax probabilities
    """
    y_true_int = np.asarray(y_true_int).astype(int)
    y_pred_probs = np.asarray(y_pred_probs, dtype=np.float32)
    y_pred = np.argmax(y_pred_probs, axis=1)

    report = classification_report(
        y_true_int, y_pred, target_names=list(class_names), output_dict=True, zero_division=0
    )
    cm = confusion_matrix(y_true_int, y_pred).tolist()
    try:
        auc = float(roc_auc_score(y_true_int, y_pred_probs[:, 1]))
    except ValueError:
        auc = None

    payload = {
        "classification_report": report,
        "confusion_matrix": cm,
        "roc_auc_leprosy_column1": auc,
        "class_names": list(class_names),
    }
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"✅ Métricas sklearn salvas em: {out_path}")
    return payload


def predict_generator_all_batches(model, generator):
    """Runs model.predict on full Keras ImageDataGenerator (shuffle should be False)."""
    generator.reset()
    steps = int(np.ceil(generator.samples / generator.batch_size))
    ys = []
    ps = []
    for _ in range(steps):
        xb, yb = next(generator)
        pb = model.predict(xb, verbose=0)
        ps.append(pb)
        ys.append(np.argmax(yb, axis=1))
    y_true = np.concatenate(ys)
    probs = np.concatenate(ps, axis=0)
    n = generator.samples
    return y_true[:n], probs[:n]


def predict_tf_dataset_all_batches(model, dataset):
    """Collects y and probs from a tf.data.Dataset yielding (x, y); y one-hot or int."""
    ys = []
    ps = []
    for xb, yb in dataset:
        pb = model.predict(xb, verbose=0)
        ps.append(pb)
        yb = yb.numpy()
        if yb.ndim == 2 and yb.shape[-1] > 1:
            ys.append(np.argmax(yb, axis=1))
        else:
            ys.append(yb.flatten())
    y_true = np.concatenate(ys)
    probs = np.concatenate(ps, axis=0)
    n = len(y_true)
    return y_true[:n], probs[:n]
