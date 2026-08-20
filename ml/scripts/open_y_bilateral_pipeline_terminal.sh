#!/usr/bin/env bash
# Atalho: abre o pipeline y_bilateral em um terminal visível (GPU obrigatória).
set -euo pipefail
ML_DIR="/home/alyssandro/Documentos/Github/leprosy_classification_models-TCC/ml"
cd "$ML_DIR"
echo "=== Pipeline y_bilateral ==="
nvidia-smi --query-gpu=name,memory.free --format=csv || {
  echo "ERRO: GPU indisponível. Abortando."
  read -r -p "Enter para fechar..."
  exit 1
}
echo
bash scripts/run_y_bilateral_pipeline.sh
echo
echo "=== Fim (exit $?) ==="
read -r -p "Enter para fechar..."
