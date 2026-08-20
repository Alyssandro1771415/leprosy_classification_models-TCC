#!/usr/bin/env bash
# Treina ResNet50 from-zero para cada variante de pré-processamento (ablação CO2Wounds-V2).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export TF_CPP_MIN_LOG_LEVEL="${TF_CPP_MIN_LOG_LEVEL:-1}"
export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"

if command -v uv >/dev/null 2>&1; then
  PYTHON_RUN=(uv run python)
else
  PY="${ROOT}/.venv/bin/python"
  if [[ ! -x "$PY" ]]; then
    PY="$(cd "$ROOT/.." && pwd)/.venv/bin/python"
  fi
  if [[ ! -x "$PY" ]]; then
    echo "ERRO: uv/.venv não encontrado. Veja ml/README.md." >&2
    exit 1
  fi
  PYTHON_RUN=("${PY}")
fi

VARIANTS=(y_only y_bilateral y_otsu y_bilateral_otsu)
# Explícito: o padrão do script Python já foi 1 no passado e quebrou as BatchNorm.
# Se estourar VRAM (RESOURCE_EXHAUSTED), rode com BATCH_SIZE=8 — nunca 1.
BATCH_SIZE="${BATCH_SIZE:-16}"
EPOCHS="${EPOCHS:-40}"
REQUIRE_GPU="${REQUIRE_GPU:-1}"
GPU_FLAG=()
if [[ "$REQUIRE_GPU" == "1" ]]; then
  GPU_FLAG=(--require-gpu)
fi

echo "=== GPU (TensorFlow) ==="
GPU_COUNT=$("${PYTHON_RUN[@]}" -c 'import tensorflow as tf; print(len(tf.config.list_physical_devices("GPU")))' 2>/dev/null || echo 0)
"${PYTHON_RUN[@]}" -c 'import tensorflow as tf; print(tf.config.list_physical_devices("GPU"))' 2>/dev/null || true

if [[ "$REQUIRE_GPU" == "1" ]] && [[ "$GPU_COUNT" -eq 0 ]]; then
    echo "" >&2
    echo "ERRO: GPU não detectada pelo TensorFlow (--require-gpu ativo)." >&2
    echo "  • Confira: nvidia-smi" >&2
    echo "  • Teste:  uv run python -c \"import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))\"" >&2
    echo "  • Se nvidia-smi OK mas TF vazio: reinicie o PC ou rode 'sudo modprobe -r nvidia_uvm && sudo modprobe nvidia_uvm'" >&2
    echo "  • Para forçar CPU (lento): REQUIRE_GPU=0 bash $0" >&2
    exit 1
fi

i=0
total=${#VARIANTS[@]}
for variant in "${VARIANTS[@]}"; do
  i=$((i + 1))
  echo ""
  echo "=== Treino ${i}/${total}: ablação ${variant} (batch=${BATCH_SIZE}, épocas=${EPOCHS}) ==="
  "${PYTHON_RUN[@]}" scripts/train_co2wounds_binary_from_zero.py \
    --data processed \
    --processed-variant "$variant" \
    --batch-size "$BATCH_SIZE" \
    --epochs "$EPOCHS" \
    "${GPU_FLAG[@]}"
done

echo ""
echo "=== Treinos de ablação concluídos ==="
