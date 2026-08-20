#!/usr/bin/env bash
# Pipeline: pré-processamento Y + Bilateral + treino ResNet50 from-zero (CO2Wounds-V2).
# Usa apenas a variante y_bilateral. Exige GPU (não há fallback para CPU).
#
# Uso:
#   bash scripts/run_y_bilateral_pipeline.sh
#   FORCE=1 bash scripts/run_y_bilateral_pipeline.sh   # reprocessa tudo do zero
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export TF_CPP_MIN_LOG_LEVEL="${TF_CPP_MIN_LOG_LEVEL:-1}"
export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1

# Libs CUDA do pip (venv), sem misturar com /usr/local/cuda do sistema
PY_FOR_LIBS="${ROOT}/.venv/bin/python"
if [[ -x "$PY_FOR_LIBS" ]]; then
  NV_LIBS=$("$PY_FOR_LIBS" - <<'PY' 2>/dev/null || true
from pathlib import Path
import site
paths = []
for sp in site.getsitepackages():
    root = Path(sp)
    paths.extend(sorted(str(p) for p in root.glob("nvidia/*/lib") if p.is_dir()))
    paths.extend(sorted(str(p) for p in root.glob("nvidia/*/lib64") if p.is_dir()))
print(":".join(paths))
PY
)
  export LD_LIBRARY_PATH="${NV_LIBS}"
else
  unset LD_LIBRARY_PATH
fi

VARIANT="y_bilateral"
FORCE="${FORCE:-0}"
LOG="${ROOT}/artifacts/logs/y_bilateral_pipeline.log"
mkdir -p "$(dirname "$LOG")"

# Saída ao vivo no terminal + cópia no log (linha a linha)
exec > >(stdbuf -oL -eL tee -a "$LOG") 2>&1

echo "========================================"
echo " CO2Wounds-V2 — Pipeline y_bilateral"
echo " $(date -Iseconds)"
echo " FORCE=${FORCE}"
echo "========================================"

# Preferir .venv direto (evita uv run ressincronizar pacotes no meio do pipeline)
if [[ -x "${ROOT}/.venv/bin/python" ]]; then
  PYTHON_RUN=("${ROOT}/.venv/bin/python" -u)
elif command -v uv >/dev/null 2>&1; then
  PYTHON_RUN=(uv run python -u)
else
  echo "ERRO: .venv/uv não encontrado. Veja ml/README.md." >&2
  exit 1
fi

echo ""
echo "=== Checagem de GPU (obrigatória) ==="
if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "ERRO: nvidia-smi não encontrado." >&2
  exit 1
fi
if ! nvidia-smi >/dev/null 2>&1 || ! ls /dev/nvidia0 >/dev/null 2>&1; then
  echo "ERRO: /dev/nvidia* ausente ou nvidia-smi falhou." >&2
  echo "  Rode o bootstrap (repara devices + TF + treino):" >&2
  echo "    bash scripts/bootstrap_gpu_and_train.sh" >&2
  exit 1
fi
nvidia-smi --query-gpu=name,driver_version,memory.total,memory.free --format=csv

GPU_COUNT=$("${PYTHON_RUN[@]}" -c 'import tensorflow as tf; print(len(tf.config.list_physical_devices("GPU")))' 2>/dev/null || echo 0)
"${PYTHON_RUN[@]}" -c 'import tensorflow as tf; print(tf.config.list_physical_devices("GPU"))' 2>/dev/null || true
if [[ "$GPU_COUNT" -eq 0 ]]; then
  echo "ERRO: TensorFlow não detectou GPU." >&2
  echo "  Rode: bash scripts/bootstrap_gpu_and_train.sh" >&2
  exit 1
fi

echo ""
echo "=== Fase 1/2: Pré-processamento (${VARIANT}) ==="
PRE_ARGS=(scripts/run_preprocessing_ablation.py --variant "$VARIANT")
if [[ "$FORCE" == "1" ]]; then
  PRE_ARGS+=(--force)
  echo "(FORCE=1: reprocessando do zero)"
else
  echo "(continuando: .npy existentes serão pulados)"
fi
"${PYTHON_RUN[@]}" "${PRE_ARGS[@]}"

echo ""
echo "=== Fase 2/2: Treino from-zero (${VARIANT}) ==="
"${PYTHON_RUN[@]}" scripts/train_co2wounds_binary_from_zero.py \
  --data processed \
  --processed-variant "$VARIANT" \
  --require-gpu \
  --batch-size "${BATCH_SIZE:-1}"

echo ""
echo "=== Pipeline concluído: $(date -Iseconds) ==="
echo "Log: $LOG"
