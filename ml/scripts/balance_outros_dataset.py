#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Balanceia a classe `outros` contra `leprosy` movendo repetições/imagens muito
similares para uma pasta de backup (histórico reversível).

Exemplos:
    # Prévia sem mover nada
    uv run python scripts/balance_outros_dataset.py --dry-run

    # Balanceia em 2 outros por leprosy (padrão) nos três splits
    uv run python scripts/balance_outros_dataset.py

    # Desfaz, devolvendo tudo do backup para `outros`
    uv run python scripts/balance_outros_dataset.py --restore
"""

import argparse

from leprosy_ml.data.balancing import (
    DEFAULT_MAX_HAMMING,
    DEFAULT_RATIO,
    SPLITS,
    balance_dataset,
    restore_from_backup,
)
from leprosy_ml.paths import data_dir


def parse_args():
    parser = argparse.ArgumentParser(description="Balanceamento manual da classe outros")
    parser.add_argument(
        "--ratio",
        type=float,
        default=DEFAULT_RATIO,
        help=f"Imagens de outros por imagem de leprosy (padrão: {DEFAULT_RATIO})",
    )
    parser.add_argument(
        "--splits",
        nargs="+",
        choices=SPLITS,
        default=list(SPLITS),
        help="Splits a balancear (padrão: train val test)",
    )
    parser.add_argument(
        "--max-hamming",
        type=int,
        default=DEFAULT_MAX_HAMMING,
        help=f"Distância dHash máxima para tratar como quase-duplicata (padrão: {DEFAULT_MAX_HAMMING})",
    )
    parser.add_argument(
        "--allocation",
        choices=["sqrt", "round_robin"],
        default="sqrt",
        help="Como dividir as vagas entre categorias (padrão: sqrt)",
    )
    parser.add_argument(
        "--keep-augmented",
        action="store_true",
        help="Mantém as cópias `aug_N_*` já gravadas na base (padrão: mandar para o backup)",
    )
    parser.add_argument("--workers", type=int, default=8, help="Threads de leitura de imagens")
    parser.add_argument("--dry-run", action="store_true", help="Só relata, não move arquivos")
    parser.add_argument("--restore", action="store_true", help="Devolve o backup para outros/")
    return parser.parse_args()


def main():
    args = parse_args()
    raw_base = data_dir("co2wounds_v2", "raw", "train_images_binary")
    backup_root = data_dir("co2wounds_v2", "backup", "outros_balanceamento")

    if args.restore:
        restore_from_backup(raw_base, backup_root, splits=tuple(args.splits))
        print("\n⚠️ Rode scripts/clean_processed_data.py depois de restaurar/rebalancear.")
        return

    balance_dataset(
        raw_base=raw_base,
        backup_root=backup_root,
        ratio=args.ratio,
        splits=tuple(args.splits),
        max_hamming=args.max_hamming,
        allocation=args.allocation,
        dry_run=args.dry_run,
        workers=args.workers,
        drop_augmented=not args.keep_augmented,
    )
    if not args.dry_run:
        print("\n➡️ Próximo passo: uv run python scripts/clean_processed_data.py")


if __name__ == "__main__":
    main()
