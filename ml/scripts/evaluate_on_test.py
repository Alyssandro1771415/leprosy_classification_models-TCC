#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Avalia modelos treinados no split de **teste**, que o treino não usa.

Os callbacks escolhem o checkpoint pelo melhor `val_auc`, e as métricas gravadas
durante o treino são do mesmo conjunto de validação — ou seja, otimistas. Os números
para o TCC devem sair daqui.

Exemplos:
    uv run python scripts/evaluate_on_test.py
    uv run python scripts/evaluate_on_test.py --variants y_bilateral y_otsu
"""

import argparse
import os

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import numpy as np

from leprosy_ml.data.co2wounds import load_npy_dataset
from leprosy_ml.evaluation.metrics import sklearn_binary_metrics_json
from leprosy_ml.models.io import load_model
from leprosy_ml.paths import metrics_dir
from leprosy_ml.preprocessing.ablation import ABLATION_VARIANTS, variant_processed_dir

CLASS_NAMES = ["leprosy", "outros"]
OUTPUT_PATTERN = "modelo_binario_co2wounds_ablation_{variant}"


def parse_args():
    parser = argparse.ArgumentParser(description="Avaliação no split de teste")
    parser.add_argument(
        "--variants",
        nargs="+",
        choices=[v.name for v in ABLATION_VARIANTS],
        default=[v.name for v in ABLATION_VARIANTS],
    )
    parser.add_argument("--batch-size", type=int, default=16)
    return parser.parse_args()


def evaluate_variant(variant: str, batch_size: int):
    output_name = OUTPUT_PATTERN.format(variant=variant)
    test_dir = variant_processed_dir(variant) / "test"
    if not test_dir.exists():
        print(f"⚠️ {variant}: split de teste ausente em {test_dir}")
        return None

    X_test, y_test = load_npy_dataset(str(test_dir))
    if len(X_test) == 0:
        print(f"⚠️ {variant}: nenhum .npy de teste")
        return None

    model = load_model(output_name, dataset="co2wounds")
    probs = model.predict(X_test, batch_size=batch_size, verbose=0)

    payload = sklearn_binary_metrics_json(
        y_test, probs, CLASS_NAMES, metrics_dir() / f"{output_name}_test_sklearn.json"
    )
    report = payload["classification_report"]
    return {
        "variante": variant,
        "n": int(len(y_test)),
        "acuracia": report["accuracy"],
        "recall_leprosy": report["leprosy"]["recall"],
        "precisao_leprosy": report["leprosy"]["precision"],
        "f1_leprosy": report["leprosy"]["f1-score"],
        "auc": payload["roc_auc_leprosy_column1"],
        "colapso": payload["predicoes_colapsadas"],
        "matriz": payload["confusion_matrix"],
    }


def main():
    args = parse_args()
    print("🧪 AVALIAÇÃO NO SPLIT DE TESTE")
    print("=" * 60)

    rows = []
    for variant in args.variants:
        print(f"\n▶ {variant}")
        result = evaluate_variant(variant, args.batch_size)
        if result:
            rows.append(result)

    if not rows:
        print("Nenhuma variante avaliada.")
        return

    print("\n📊 RESULTADOS (teste)")
    print("=" * 88)
    header = f"{'variante':18s} {'acc':>7s} {'rec_lep':>8s} {'prec_lep':>9s} {'f1_lep':>7s} {'auc':>7s}"
    print(header)
    print("-" * 88)
    for r in sorted(rows, key=lambda r: -(r["auc"] or 0)):
        flag = "  ❌ colapso" if r["colapso"] else ""
        print(
            f"{r['variante']:18s} {r['acuracia']:7.4f} {r['recall_leprosy']:8.4f} "
            f"{r['precisao_leprosy']:9.4f} {r['f1_leprosy']:7.4f} "
            f"{(r['auc'] or float('nan')):7.4f}{flag}"
        )
    print("-" * 88)
    for r in rows:
        print(f"  {r['variante']}: matriz de confusão {r['matriz']} (n={r['n']})")
    print(f"\nJSONs em: {metrics_dir()}/*_test_sklearn.json")


if __name__ == "__main__":
    main()
