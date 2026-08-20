#!/usr/bin/env bash
# Executa os 4 cenários CO2Wounds-V2 com --require-gpu (falha se não houver GPU TF).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export TF_CPP_MIN_LOG_LEVEL="${TF_CPP_MIN_LOG_LEVEL:-1}"

if command -v uv >/dev/null 2>&1; then
  PYTHON_RUN=(uv run python)
else
  PY="${ROOT}/.venv/bin/python"
  if [[ ! -x "$PY" ]]; then
    echo "ERRO: uv não está no PATH e ${PY} não existe. Veja ml/README.md." >&2
    exit 1
  fi
  PYTHON_RUN=("${PY}")
fi

echo "=== GPU (TensorFlow) ==="
"${PYTHON_RUN[@]}" -c 'import tensorflow as tf; print(tf.config.list_physical_devices("GPU"))'
echo "=== 1/4 transfer raw ==="
"${PYTHON_RUN[@]}" scripts/train_co2wounds_binary_transfer.py --data raw --require-gpu
echo "=== 2/4 transfer processed ==="
"${PYTHON_RUN[@]}" scripts/train_co2wounds_binary_transfer.py --data processed --require-gpu
echo "=== 3/4 from-zero processed ==="
"${PYTHON_RUN[@]}" scripts/train_co2wounds_binary_from_zero.py --data processed --require-gpu
echo "=== 4/4 from-zero raw ==="
"${PYTHON_RUN[@]}" scripts/train_co2wounds_binary_from_zero.py --data raw --require-gpu
echo "=== Concluído ==="
