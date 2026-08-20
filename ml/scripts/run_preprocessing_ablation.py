#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera as 4 variantes de pré-processamento para ablação CO2Wounds-V2."""

import argparse

from leprosy_ml.preprocessing.ablation import ABLATION_VARIANTS, batch_process_ablation


def main():
    p = argparse.ArgumentParser(description="Pré-processamento ablação CO2Wounds-V2")
    p.add_argument(
        "--variant",
        choices=[v.name for v in ABLATION_VARIANTS],
        action="append",
        help="Processar só variantes indicadas (padrão: todas)",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Reprocessar mesmo se .npy já existir (remove pasta de saída do split)",
    )
    args = p.parse_args()

    if args.variant:
        selected = {v.name for v in ABLATION_VARIANTS}
        unknown = set(args.variant) - selected
        if unknown:
            raise SystemExit(f"Variantes desconhecidas: {unknown}")
        variants = tuple(v for v in ABLATION_VARIANTS if v.name in args.variant)
    else:
        variants = ABLATION_VARIANTS

    batch_process_ablation(variants=variants, force=args.force)


if __name__ == "__main__":
    main()
