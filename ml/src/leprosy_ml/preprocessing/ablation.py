# -*- coding: utf-8 -*-
"""Variantes de pré-processamento (canal Y) para estudo de ablação CO2Wounds-V2."""

from dataclasses import dataclass

from leprosy_ml.paths import data_dir, get_ml_root
from leprosy_ml.preprocessing.pipeline import process_directory


@dataclass(frozen=True)
class PreprocessingVariant:
    name: str
    label: str
    apply_bilateral: bool
    apply_otsu: bool


ABLATION_VARIANTS: tuple[PreprocessingVariant, ...] = (
    PreprocessingVariant("y_only", "Canal Y", False, False),
    PreprocessingVariant("y_bilateral", "Canal Y + Bilateral", True, False),
    PreprocessingVariant("y_otsu", "Canal Y + Otsu", False, True),
    PreprocessingVariant(
        "y_bilateral_otsu",
        "Canal Y + Bilateral + Otsu",
        True,
        True,
    ),
)


def variant_processed_dir(variant_name: str):
    """Raiz train_images_binary para uma variante de ablação."""
    return data_dir("co2wounds_v2", "processed", "ablation", variant_name, "train_images_binary")


def batch_process_ablation(variants=None, force: bool = False):
    """
    Gera .npy para cada variante de pré-processamento.

    Saída: data/co2wounds_v2/processed/ablation/{variant}/train_images_binary/{train,val,test}/...
    """
    if variants is None:
        variants = ABLATION_VARIANTS

    ml_root = get_ml_root()
    base_input = data_dir("co2wounds_v2", "raw", "train_images_binary")
    splits = ["train", "val", "test"]

    print("🔄 ABLAÇÃO DE PRÉ-PROCESSAMENTO — CO2Wounds-V2")
    print("=" * 60)
    print(f"📁 ML root: {ml_root}")
    print(f"📥 Input:   {base_input}")

    summary = []

    for variant in variants:
        print(f"\n{'=' * 60}")
        print(f"▶ Variante: {variant.name} ({variant.label})")
        print(f"   bilateral={variant.apply_bilateral}  otsu={variant.apply_otsu}")

        base_output = variant_processed_dir(variant.name)
        total_stats = {"total": 0, "processed": 0, "errors": 0, "skipped": 0}

        for split in splits:
            input_dir = base_input / split
            output_dir = base_output / split

            if not input_dir.exists():
                print(f"   ❌ Split ausente: {input_dir}")
                continue

            if force and output_dir.exists():
                import shutil

                shutil.rmtree(output_dir)

            stats = process_directory(
                input_dir,
                output_dir,
                apply_otsu=variant.apply_otsu,
                apply_bilateral=variant.apply_bilateral,
            )
            for key in total_stats:
                total_stats[key] += stats[key]

            print(
                f"   {split.upper()}: processadas={stats['processed']} "
                f"puladas={stats['skipped']} erros={stats['errors']}"
            )

        summary.append((variant.name, total_stats))
        print(
            f"   ✅ Total variante: processadas={total_stats['processed']} "
            f"puladas={total_stats['skipped']} erros={total_stats['errors']}"
        )

    print(f"\n{'=' * 60}")
    print("📊 RESUMO ABLAÇÃO")
    for name, stats in summary:
        print(f"  {name}: {stats['processed']} novas, {stats['skipped']} já existiam, {stats['errors']} erros")

    return summary
