# -*- coding: utf-8 -*-
"""Post-training binary classification metrics (sklearn + JSON export)."""

import json
from pathlib import Path

import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

OVERFITTING_ACC_GAP_THRESHOLD = 0.10
OVERFITTING_LOSS_RATIO_THRESHOLD = 1.15
# Margem sobre o baseline da classe majoritária para considerar que houve aprendizado
COLLAPSE_MARGIN = 0.02


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

    # Modelo degenerado: prevê sempre a mesma classe. A acurácia fica igual à
    # proporção da classe majoritária e engana quem olhar só esse número.
    predicted_classes = sorted(int(c) for c in np.unique(y_pred))
    collapsed = len(predicted_classes) < len(class_names)

    payload = {
        "classification_report": report,
        "confusion_matrix": cm,
        "roc_auc_leprosy_column1": auc,
        "class_names": list(class_names),
        "predicoes_colapsadas": collapsed,
        "classes_previstas": [list(class_names)[c] for c in predicted_classes],
    }
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"✅ Métricas sklearn salvas em: {out_path}")
    if collapsed:
        only = ", ".join(payload["classes_previstas"])
        print(
            f"❌ COLAPSO: o modelo só prevê '{only}'. A acurácia reflete apenas a classe "
            f"majoritária — recall das demais classes é zero."
        )
    return payload


def overfitting_report(
    history,
    out_path,
    class_counts=None,
    acc_gap_threshold=OVERFITTING_ACC_GAP_THRESHOLD,
    loss_ratio_threshold=OVERFITTING_LOSS_RATIO_THRESHOLD,
):
    """
    Diagnóstico de overfitting a partir do `history` do Keras, salvo em JSON.

    Sinais avaliados:
    - `colapso`: o modelo nunca superou o baseline da classe majoritária, ou seja,
      aprendeu apenas a chutar sempre a classe mais frequente. Precisa vir antes dos
      demais sinais: um modelo degenerado tem gap zero e passaria por "bem generalizado".
      Há duas variantes: `colapso_classe_majoritaria` (nem treino nem validação saem do
      baseline) e `colapso_validacao` (o treino ajusta, mas a validação nunca supera o
      baseline — caso em que o checkpoint restaurado costuma prever uma única classe);
    - `gap_acuracia`: acurácia de treino menos a de validação (fim do treino);
    - `gap_acuracia_maximo`: maior gap observado e em qual época;
    - `razao_val_loss_final_melhor`: quanto a val_loss final subiu acima do mínimo
      (divergência típica de overfitting, mesmo com acurácia alta);
    - `epocas_apos_melhor`: épocas treinadas depois do melhor ponto de validação.

    `class_counts` (ex.: {"leprosy": 485, "outros": 970}) é usado para calcular o
    baseline da classe majoritária e fica registrado para auditar o desequilíbrio.
    """
    hist = getattr(history, "history", history)
    acc = [float(v) for v in hist["accuracy"]]
    val_acc = [float(v) for v in hist["val_accuracy"]]
    loss = [float(v) for v in hist["loss"]]
    val_loss = [float(v) for v in hist["val_loss"]]

    gaps = [a - v for a, v in zip(acc, val_acc)]
    best_epoch = int(np.argmin(val_loss))
    max_gap_epoch = int(np.argmax(gaps))
    best_val_loss = val_loss[best_epoch]
    loss_ratio = float(val_loss[-1] / best_val_loss) if best_val_loss > 0 else None

    majority_baseline = None
    collapsed = False
    collapsed_val = False
    if class_counts:
        total = sum(class_counts.values())
        if total > 0:
            majority_baseline = max(class_counts.values()) / total
            limit = majority_baseline + COLLAPSE_MARGIN
            collapsed = max(max(acc), max(val_acc)) <= limit
            collapsed_val = max(val_acc) <= limit

    diverged = loss_ratio is not None and loss_ratio > loss_ratio_threshold
    wide_gap = gaps[-1] > acc_gap_threshold
    if collapsed or collapsed_val:
        verdict = "colapso"
    elif wide_gap and diverged:
        verdict = "overfitting"
    elif wide_gap or diverged:
        verdict = "atencao"
    else:
        verdict = "ok"

    payload = {
        "veredito": verdict,
        "colapso_classe_majoritaria": collapsed,
        "colapso_validacao": collapsed_val,
        "baseline_classe_majoritaria": majority_baseline,
        "epocas": len(acc),
        "acuracia_treino_final": acc[-1],
        "acuracia_val_final": val_acc[-1],
        "loss_treino_final": loss[-1],
        "loss_val_final": val_loss[-1],
        "gap_acuracia": gaps[-1],
        "gap_acuracia_maximo": max(gaps),
        "epoca_gap_maximo": max_gap_epoch + 1,
        "melhor_epoca_val_loss": best_epoch + 1,
        "melhor_val_loss": best_val_loss,
        "razao_val_loss_final_melhor": loss_ratio,
        "epocas_apos_melhor": len(val_loss) - best_epoch - 1,
        "limiares": {
            "gap_acuracia": acc_gap_threshold,
            "razao_val_loss": loss_ratio_threshold,
            "margem_colapso": COLLAPSE_MARGIN,
        },
        "distribuicao_classes_treino": class_counts,
        "curvas": {
            "accuracy": acc,
            "val_accuracy": val_acc,
            "loss": loss,
            "val_loss": val_loss,
            "gap_acuracia": gaps,
        },
    }

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    icons = {"colapso": "❌", "overfitting": "❌", "atencao": "⚠️", "ok": "✅"}
    print(f"\n{icons[verdict]} Diagnóstico de overfitting: {verdict.upper()}")
    if collapsed:
        print(
            f"   o modelo não superou o baseline da classe majoritária "
            f"({majority_baseline:.4f}) — está prevendo sempre a mesma classe"
        )
    elif collapsed_val:
        print(
            f"   a acurácia de validação nunca superou o baseline da classe majoritária "
            f"({majority_baseline:.4f}), embora o treino tenha chegado a {max(acc):.4f} — "
            f"o checkpoint restaurado tende a prever uma única classe"
        )
    print(f"   gap de acurácia final: {gaps[-1]:.4f} (limiar {acc_gap_threshold})")
    print(f"   gap máximo: {max(gaps):.4f} na época {max_gap_epoch + 1}")
    print(
        f"   val_loss final/melhor: {'n/d' if loss_ratio is None else f'{loss_ratio:.3f}'} "
        f"(melhor época: {best_epoch + 1}, +{len(val_loss) - best_epoch - 1} épocas depois)"
    )
    if class_counts:
        print(f"   distribuição de treino: {class_counts}")
    print(f"   relatório salvo em: {out_path}")
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
