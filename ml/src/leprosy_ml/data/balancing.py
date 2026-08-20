# -*- coding: utf-8 -*-
"""
Balanceamento manual da classe `outros` por similaridade visual.

A classe `outros` (Atlas Dermatology + coleta web) é ~15x maior que `leprosy`,
o que enviesa o treino. Este módulo escolhe, para cada split, um subconjunto de
`outros` com tamanho `ratio * n_leprosy` priorizando diversidade visual e move o
excedente para uma pasta de backup (histórico reversível), registrando o motivo
de cada remoção em manifesto.

Critérios de remoção, em ordem de prioridade:
1. `imagem_aumentada` — cópia sintética `aug_N_<original>` gravada na base; o treino
   já aplica augmentation em tempo de execução, e `leprosy` não tem cópias assim;
2. `duplicata_exata` — mesmo hash MD5 do arquivo;
3. `quase_duplicata` — dHash a distância de Hamming <= limiar (fotos da mesma lesão);
4. `vazamento_entre_splits` — quase-duplicata de uma imagem mantida em val/test;
5. `excedente_similaridade` — excedente da cota da categoria, escolhido por ser o
   mais próximo das imagens já mantidas.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp")

# Cópias sintéticas já gravadas na base: `Acne__aug_83_pigmentation_0_1906.jpeg`
AUGMENTED_PATTERN = re.compile(r"(?:^|__|_)aug_\d+_", re.IGNORECASE)

DHASH_SIZE = 8
DESCRIPTOR_SIZE = 16
DEFAULT_MAX_HAMMING = 6
DEFAULT_RATIO = 2.0
SPLITS = ("train", "val", "test")


def list_images(directory: Path) -> list[Path]:
    """Imagens de um diretório (ordem estável, extensões conhecidas)."""
    if not directory.exists():
        return []
    return sorted(
        p for p in directory.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )


def filename_category(path: Path | str) -> str:
    """
    Categoria da doença embutida no nome do arquivo.

    Dois padrões convivem na base:
    - coleta web: `Eczema__foo.jpeg` -> `eczema`
    - Atlas: `05AtopicFace010504.jpg` -> `atopic` (prefixo do capítulo é descartado)
    """
    stem = Path(path).stem
    if "__" in stem:
        prefix = stem.split("__", 1)[0]
    else:
        prefix = re.sub(r"^\d+", "", stem)
    tokens = re.findall(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+", prefix)
    return tokens[0].lower() if tokens else "sem_categoria"


def is_augmented(path: Path | str) -> bool:
    return bool(AUGMENTED_PATTERN.search(Path(path).name))


def original_of_augmented(path: Path | str) -> str:
    """Nome do arquivo original correspondente a uma cópia `aug_N_<original>`."""
    name = Path(path).name
    return AUGMENTED_PATTERN.sub(lambda m: m.group(0)[: m.group(0).index("aug_")], name, count=1)


@dataclass
class Fingerprint:
    path: Path
    category: str
    md5: str
    dhash: np.ndarray  # (64,) uint8 com bits 0/1
    descriptor: np.ndarray  # (256,) float32 z-normalizado
    pixels: int
    bytes: int


def _fingerprint(path: Path) -> Fingerprint | None:
    try:
        raw = path.read_bytes()
        with Image.open(path) as img:
            width, height = img.size
            gray = img.convert("L")
            hash_img = np.asarray(
                gray.resize((DHASH_SIZE + 1, DHASH_SIZE), Image.LANCZOS), dtype=np.int16
            )
            small = np.asarray(
                gray.resize((DESCRIPTOR_SIZE, DESCRIPTOR_SIZE), Image.LANCZOS), dtype=np.float32
            )
    except Exception as exc:  # imagem corrompida não deve derrubar o lote
        print(f"⚠️ Falha ao ler {path.name}: {exc}")
        return None

    bits = (hash_img[:, 1:] > hash_img[:, :-1]).astype(np.uint8).flatten()

    descriptor = small.flatten()
    descriptor -= descriptor.mean()
    norm = float(np.linalg.norm(descriptor))
    if norm > 0:
        descriptor /= norm

    return Fingerprint(
        path=path,
        category=filename_category(path),
        md5=hashlib.md5(raw).hexdigest(),
        dhash=bits,
        descriptor=descriptor.astype(np.float32),
        pixels=width * height,
        bytes=len(raw),
    )


def compute_fingerprints(paths: list[Path], workers: int = 8) -> list[Fingerprint]:
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(_fingerprint, paths))
    return [fp for fp in results if fp is not None]


def hamming_matrix(bits_a: np.ndarray, bits_b: np.ndarray) -> np.ndarray:
    """Distâncias de Hamming entre dois conjuntos de vetores binários (0/1)."""
    a = bits_a.astype(np.int16)
    b = bits_b.astype(np.int16)
    return a.sum(1)[:, None] + b.sum(1)[None, :] - 2 * (a @ b.T)


def _quality_key(fp: Fingerprint) -> tuple[int, int, int, str]:
    """
    Representante de um grupo de duplicatas: original antes de cópia aumentada,
    depois maior resolução e maior arquivo.
    """
    return (0 if is_augmented(fp.path) else 1, fp.pixels, fp.bytes, fp.path.name)


def allocate_quotas(counts: dict[str, int], target: int, mode: str = "sqrt") -> dict[str, int]:
    """
    Distribui `target` vagas entre categorias.

    - `sqrt`: cota proporcional a sqrt(nº disponível), garantindo 1 por categoria
      (mantém as categorias grandes mais representadas sem sufocar a cauda longa);
    - `round_robin`: 1 vaga por categoria por rodada (diversidade máxima).
    """
    quotas = {name: 0 for name in counts}
    capacity = {name: counts[name] for name in counts}
    total_capacity = sum(capacity.values())
    remaining = min(target, total_capacity)

    if mode == "sqrt":
        weights = {name: float(np.sqrt(n)) for name, n in capacity.items() if n > 0}
        total_weight = sum(weights.values())
        for name, weight in weights.items():
            share = int(remaining * weight / total_weight) if total_weight else 0
            quotas[name] = min(capacity[name], max(1, share))

        # A cota mínima de 1 por categoria pode estourar o alvo: reduz as maiores
        # primeiro e, se ainda não couber, zera as categorias mais raras.
        overflow = sum(quotas.values()) - remaining
        while overflow > 0:
            reducible = [name for name in quotas if quotas[name] > 1]
            if not reducible:
                break
            for name in sorted(reducible, key=lambda n: (-quotas[n], n)):
                if overflow == 0:
                    break
                quotas[name] -= 1
                overflow -= 1
        for name in sorted(quotas, key=lambda n: (capacity[n], n)):
            if overflow <= 0:
                break
            if quotas[name] == 1:
                quotas[name] = 0
                overflow -= 1
        remaining -= sum(quotas.values())

    order = sorted(capacity, key=lambda n: (-(capacity[n] - quotas[n]), n))
    while remaining > 0:
        progressed = False
        for name in order:
            if remaining == 0:
                break
            if quotas[name] < capacity[name]:
                quotas[name] += 1
                remaining -= 1
                progressed = True
        if not progressed:
            break
    return quotas


def select_diverse(descriptors: np.ndarray, quota: int) -> list[int]:
    """
    Farthest-point sampling: começa pelo medoide (imagem mais representativa) e
    adiciona sempre a mais distante do que já foi escolhido.

    Retorna índices na ordem de seleção.
    """
    n = len(descriptors)
    if quota >= n:
        return list(range(n))
    if quota <= 0:
        return []

    distances = np.sqrt(
        np.maximum(
            0.0,
            (descriptors**2).sum(1)[:, None]
            + (descriptors**2).sum(1)[None, :]
            - 2 * descriptors @ descriptors.T,
        )
    )
    selected = [int(np.argmin(distances.sum(1)))]
    min_dist = distances[selected[0]].copy()
    min_dist[selected[0]] = -np.inf
    for _ in range(quota - 1):
        nxt = int(np.argmax(min_dist))
        selected.append(nxt)
        min_dist = np.minimum(min_dist, distances[nxt])
        min_dist[nxt] = -np.inf
    return selected


@dataclass
class Decision:
    path: Path
    split: str
    category: str
    action: str  # "manter" | "mover"
    reason: str
    reference: str = ""
    distance: float | None = None


@dataclass
class SplitPlan:
    split: str
    n_leprosy: int
    target: int
    decisions: list[Decision] = field(default_factory=list)
    kept: list[Fingerprint] = field(default_factory=list)

    @property
    def moved(self) -> list[Decision]:
        return [d for d in self.decisions if d.action == "mover"]

    def reason_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for decision in self.moved:
            counts[decision.reason] = counts.get(decision.reason, 0) + 1
        return counts


def plan_split(
    split: str,
    outros_dir: Path,
    n_leprosy: int,
    ratio: float,
    max_hamming: int,
    allocation: str,
    claimed: list[Fingerprint],
    workers: int = 8,
    drop_augmented: bool = True,
) -> SplitPlan:
    """Decide, para um split, quais imagens de `outros` ficam e quais vão para backup."""
    target = int(round(n_leprosy * ratio))
    paths = list_images(outros_dir)
    print(f"\n▶ {split}: {len(paths)} outros | {n_leprosy} leprosy | alvo = {target}")

    plan = SplitPlan(split=split, n_leprosy=n_leprosy, target=target)
    if not paths:
        print("   ⚠️ Nenhuma imagem encontrada")
        return plan

    # 0) cópias sintéticas gravadas na base (não existem em `leprosy`)
    if drop_augmented:
        existing = {p.name for p in paths}
        augmented = [p for p in paths if is_augmented(p)]
        for path in augmented:
            original = original_of_augmented(path)
            plan.decisions.append(
                Decision(
                    path,
                    split,
                    filename_category(path),
                    "mover",
                    "imagem_aumentada",
                    original if original in existing else "",
                )
            )
        paths = [p for p in paths if not is_augmented(p)]
        print(f"   cópias aumentadas removidas: {len(augmented)} | restam {len(paths)}")

    fingerprints = compute_fingerprints(paths, workers=workers)
    print(f"   assinaturas calculadas: {len(fingerprints)}")

    # 1) duplicatas exatas (MD5)
    survivors: list[Fingerprint] = []
    by_md5: dict[str, Fingerprint] = {}
    for fp in sorted(fingerprints, key=_quality_key, reverse=True):
        original = by_md5.get(fp.md5)
        if original is None:
            by_md5[fp.md5] = fp
            survivors.append(fp)
        else:
            plan.decisions.append(
                Decision(fp.path, split, fp.category, "mover", "duplicata_exata", original.path.name, 0.0)
            )

    # 2) quase-duplicatas por dHash, dentro de cada categoria
    deduped: list[Fingerprint] = []
    for category in sorted({fp.category for fp in survivors}):
        group = sorted(
            (fp for fp in survivors if fp.category == category), key=_quality_key, reverse=True
        )
        bits = np.stack([fp.dhash for fp in group])
        distances = hamming_matrix(bits, bits)
        representative_of: dict[int, int] = {}
        for i in range(len(group)):
            if i in representative_of:
                continue
            deduped.append(group[i])
            close = np.where(distances[i] <= max_hamming)[0]
            for j in close:
                j = int(j)
                if j <= i or j in representative_of:
                    continue
                representative_of[j] = i
                plan.decisions.append(
                    Decision(
                        group[j].path,
                        split,
                        category,
                        "mover",
                        "quase_duplicata",
                        group[i].path.name,
                        float(distances[i, j]),
                    )
                )

    # 3) vazamento: quase-duplicatas de imagens mantidas em splits já processados
    candidates = deduped
    if claimed:
        claimed_bits = np.stack([fp.dhash for fp in claimed])
        candidate_bits = np.stack([fp.dhash for fp in candidates])
        distances = hamming_matrix(candidate_bits, claimed_bits)
        nearest = distances.argmin(1)
        remaining: list[Fingerprint] = []
        for i, fp in enumerate(candidates):
            best = int(nearest[i])
            if distances[i, best] <= max_hamming:
                plan.decisions.append(
                    Decision(
                        fp.path,
                        split,
                        fp.category,
                        "mover",
                        "vazamento_entre_splits",
                        claimed[best].path.name,
                        float(distances[i, best]),
                    )
                )
            else:
                remaining.append(fp)
        candidates = remaining

    # 4) cota por categoria + seleção diversa
    by_category: dict[str, list[Fingerprint]] = {}
    for fp in candidates:
        by_category.setdefault(fp.category, []).append(fp)

    counts = {name: len(items) for name, items in by_category.items()}
    quotas = allocate_quotas(counts, target, mode=allocation)

    for category, items in sorted(by_category.items()):
        quota = quotas.get(category, 0)
        descriptors = np.stack([fp.descriptor for fp in items])
        keep_idx = select_diverse(descriptors, quota)
        keep_set = set(keep_idx)
        for idx in keep_idx:
            plan.kept.append(items[idx])
            plan.decisions.append(
                Decision(items[idx].path, split, category, "manter", "selecionada_diversidade")
            )
        drop_idx = [i for i in range(len(items)) if i not in keep_set]
        if not drop_idx:
            continue
        if keep_idx:
            kept_desc = descriptors[keep_idx]
            drop_desc = descriptors[drop_idx]
            dist = np.sqrt(
                np.maximum(
                    0.0,
                    (drop_desc**2).sum(1)[:, None]
                    + (kept_desc**2).sum(1)[None, :]
                    - 2 * drop_desc @ kept_desc.T,
                )
            )
            nearest = dist.argmin(1)
        else:
            nearest = None
        for row, idx in enumerate(drop_idx):
            reference = ""
            distance = None
            if nearest is not None:
                reference = items[keep_idx[int(nearest[row])]].path.name
                distance = float(dist[row, int(nearest[row])])
            plan.decisions.append(
                Decision(
                    items[idx].path,
                    split,
                    category,
                    "mover",
                    "excedente_similaridade",
                    reference,
                    distance,
                )
            )

    kept_total = len(plan.kept)
    print(f"   mantidas: {kept_total} | movidas: {len(plan.moved)} | categorias mantidas: {len(set(fp.category for fp in plan.kept))}")
    for reason, count in sorted(plan.reason_counts().items(), key=lambda kv: -kv[1]):
        print(f"     - {reason}: {count}")
    return plan


def _write_manifest(backup_root: Path, plans: list[SplitPlan], meta: dict) -> Path:
    backup_root.mkdir(parents=True, exist_ok=True)
    manifest = backup_root / "manifesto_balanceamento.csv"
    new_file = not manifest.exists()
    with open(manifest, "a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        if new_file:
            writer.writerow(
                ["data", "split", "arquivo", "categoria", "motivo", "referencia", "distancia"]
            )
        for plan in plans:
            for decision in plan.moved:
                writer.writerow(
                    [
                        meta["executado_em"],
                        decision.split,
                        decision.path.name,
                        decision.category,
                        decision.reason,
                        decision.reference,
                        "" if decision.distance is None else f"{decision.distance:.4f}",
                    ]
                )

    summary = {
        **meta,
        "splits": {
            plan.split: {
                "leprosy": plan.n_leprosy,
                "alvo_outros": plan.target,
                "outros_mantidas": len(plan.kept),
                "outros_movidas": len(plan.moved),
                "categorias_mantidas": sorted({fp.category for fp in plan.kept}),
                "motivos": plan.reason_counts(),
            }
            for plan in plans
        },
    }
    with open(backup_root / "resumo_balanceamento.json", "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)
    return manifest


def balance_dataset(
    raw_base: Path,
    backup_root: Path,
    ratio: float = DEFAULT_RATIO,
    splits: tuple[str, ...] = SPLITS,
    max_hamming: int = DEFAULT_MAX_HAMMING,
    allocation: str = "sqrt",
    dry_run: bool = False,
    workers: int = 8,
    drop_augmented: bool = True,
) -> list[SplitPlan]:
    """
    Balanceia `outros` contra `leprosy` em cada split, movendo o excedente ao backup.

    Val e test são planejados antes de train para que qualquer imagem de treino
    parecida com uma imagem de avaliação seja descartada (evita vazamento).
    """
    order = [s for s in ("val", "test", "train") if s in splits]
    claimed: list[Fingerprint] = []
    plans: list[SplitPlan] = []

    print("🔄 BALANCEAMENTO DA CLASSE `outros`")
    print("=" * 60)
    print(f"📥 Base: {raw_base}")
    print(f"💾 Backup: {backup_root}")
    print(f"⚖️  Proporção outros:leprosy = {ratio}:1 | alocação = {allocation} | dHash <= {max_hamming}")
    if dry_run:
        print("🧪 dry-run: nenhum arquivo será movido")

    for split in order:
        n_leprosy = len(list_images(raw_base / split / "leprosy"))
        plan = plan_split(
            split=split,
            outros_dir=raw_base / split / "outros",
            n_leprosy=n_leprosy,
            ratio=ratio,
            max_hamming=max_hamming,
            allocation=allocation,
            claimed=claimed,
            workers=workers,
            drop_augmented=drop_augmented,
        )
        plans.append(plan)
        claimed.extend(plan.kept)

    meta = {
        "executado_em": datetime.now().isoformat(timespec="seconds"),
        "proporcao_outros_por_leprosy": ratio,
        "alocacao": allocation,
        "limiar_dhash": max_hamming,
        "remove_imagens_aumentadas": drop_augmented,
        "dry_run": dry_run,
    }

    if dry_run:
        total = sum(len(plan.moved) for plan in plans)
        print(f"\n🧪 dry-run concluído: {total} imagens seriam movidas")
        return plans

    moved_bytes = 0
    for plan in plans:
        destination = backup_root / plan.split / "outros"
        destination.mkdir(parents=True, exist_ok=True)
        for decision in plan.moved:
            if not decision.path.exists():
                continue
            target_path = destination / decision.path.name
            if target_path.exists():
                target_path = destination / f"{decision.path.stem}__dup{decision.path.suffix}"
            moved_bytes += decision.path.stat().st_size
            shutil.move(str(decision.path), str(target_path))

    manifest = _write_manifest(backup_root, plans, meta)

    print("\n📊 RESUMO")
    print("=" * 60)
    for plan in plans:
        remaining = len(list_images(raw_base / plan.split / "outros"))
        print(
            f"  {plan.split}: outros {remaining} vs leprosy {plan.n_leprosy} "
            f"| movidas {len(plan.moved)}"
        )
    print(f"  espaço movido para backup: {moved_bytes / 1e6:.1f} MB")
    print(f"  manifesto: {manifest}")
    return plans


def restore_from_backup(raw_base: Path, backup_root: Path, splits: tuple[str, ...] = SPLITS) -> int:
    """Devolve as imagens do backup para `outros` (desfaz o balanceamento)."""
    restored = 0
    for split in splits:
        source = backup_root / split / "outros"
        destination = raw_base / split / "outros"
        if not source.exists():
            continue
        destination.mkdir(parents=True, exist_ok=True)
        for path in list_images(source):
            shutil.move(str(path), str(destination / path.name))
            restored += 1
        print(f"  {split}: {restored} restauradas até agora")
    print(f"↩️  Total restaurado: {restored}")
    return restored
