#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove arquivos .npy órfãos das pastas pré-processadas.

Um .npy é órfão quando a imagem original correspondente não existe mais em
`raw/train_images_binary/{split}/{classe}/` — o caso típico depois de rebalancear
`outros` (scripts/balance_outros_dataset.py). Como o pré-processamento é
reprodutível, os órfãos são apagados em vez de arquivados.

Exemplos:
    uv run python scripts/clean_processed_data.py --dry-run
    uv run python scripts/clean_processed_data.py
"""

import argparse
from pathlib import Path

from leprosy_ml.data.balancing import IMAGE_EXTENSIONS
from leprosy_ml.paths import data_dir

SPLITS = ("train", "val", "test")


def processed_roots(processed_base: Path) -> list[Path]:
    """Raízes `train_images_binary` de processed/ e de cada variante de ablação."""
    roots = []
    direct = processed_base / "train_images_binary"
    if direct.exists():
        roots.append(direct)
    ablation = processed_base / "ablation"
    if ablation.exists():
        for variant in sorted(p for p in ablation.iterdir() if p.is_dir()):
            root = variant / "train_images_binary"
            if root.exists():
                roots.append(root)
    return roots


def raw_stems(raw_class_dir: Path) -> set[str]:
    if not raw_class_dir.exists():
        return set()
    return {
        p.stem for p in raw_class_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    }


def clean_root(root: Path, raw_base: Path, dry_run: bool) -> tuple[int, int, int]:
    """Retorna (órfãos, bytes liberados, .npy restantes) de uma raiz processada."""
    orphans = 0
    freed = 0
    remaining = 0

    for split in SPLITS:
        split_dir = root / split
        if not split_dir.exists():
            continue
        for class_dir in sorted(p for p in split_dir.iterdir() if p.is_dir()):
            valid = raw_stems(raw_base / split / class_dir.name)
            class_orphans = 0
            class_kept = 0
            for npy in sorted(class_dir.glob("*.npy")):
                if npy.stem in valid:
                    class_kept += 1
                    continue
                class_orphans += 1
                freed += npy.stat().st_size
                if not dry_run:
                    npy.unlink()
            orphans += class_orphans
            remaining += class_kept
            print(
                f"   {split}/{class_dir.name}: {class_kept} válidos, {class_orphans} órfãos "
                f"(raw: {len(valid)} imagens)"
            )
    return orphans, freed, remaining


def parse_args():
    parser = argparse.ArgumentParser(description="Limpa .npy órfãos das pastas processed")
    parser.add_argument("--dry-run", action="store_true", help="Só relata, não apaga")
    return parser.parse_args()


def main():
    args = parse_args()
    raw_base = data_dir("co2wounds_v2", "raw", "train_images_binary")
    processed_base = data_dir("co2wounds_v2", "processed")

    roots = processed_roots(processed_base)
    print("🧹 LIMPEZA DE .npy ÓRFÃOS")
    print("=" * 60)
    print(f"📥 Raw de referência: {raw_base}")
    if args.dry_run:
        print("🧪 dry-run: nada será apagado")
    if not roots:
        print("Nenhuma pasta processada encontrada — nada a fazer.")
        return

    total_orphans = 0
    total_freed = 0
    for root in roots:
        print(f"\n▶ {root.relative_to(processed_base.parent)}")
        orphans, freed, remaining = clean_root(root, raw_base, args.dry_run)
        total_orphans += orphans
        total_freed += freed
        verb = "seriam removidos" if args.dry_run else "removidos"
        print(f"   {verb}: {orphans} órfãos ({freed / 1e6:.1f} MB) | válidos: {remaining}")

    print("\n📊 RESUMO")
    print("=" * 60)
    print(f"  órfãos: {total_orphans}")
    print(f"  espaço liberado: {total_freed / 1e6:.1f} MB")
    if not args.dry_run and total_orphans:
        print("\n➡️ Regere os .npy faltantes: uv run python scripts/run_preprocessing_ablation.py")


if __name__ == "__main__":
    main()
