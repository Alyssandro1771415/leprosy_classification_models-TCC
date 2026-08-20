#!/usr/bin/env bash
# Pipeline completo: pré-processamento ablação (4 variantes) + treino from-zero (4 modelos).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export TF_CPP_MIN_LOG_LEVEL="${TF_CPP_MIN_LOG_LEVEL:-1}"
export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"
LOG="${ROOT}/artifacts/logs/ablation_pipeline.log"
mkdir -p "$(dirname "$LOG")"

exec > >(tee -a "$LOG") 2>&1

echo "========================================"
echo " CO2Wounds-V2 — Pipeline de Ablação"
echo " $(date -Iseconds)"
echo "========================================"

if command -v uv >/dev/null 2>&1; then
  PYTHON_RUN=(uv run python)
else
  PY="${ROOT}/.venv/bin/python"
  if [[ ! -x "$PY" ]]; then
    PY="$(cd "$ROOT/.." && pwd)/.venv/bin/python"
  fi
  PYTHON_RUN=("${PY}")
fi

echo ""
echo "=== Fase 1/2: Pré-processamento (4 variantes) ==="
"${PYTHON_RUN[@]}" scripts/run_preprocessing_ablation.py

echo ""
echo "=== Fase 2/2: Treino from-zero (4 variantes) ==="
bash scripts/run_co2wounds_training_ablation.sh

echo ""
echo "=== Pipeline concluído: $(date -Iseconds) ==="
echo "Log: $LOG"
