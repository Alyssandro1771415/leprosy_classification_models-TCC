#!/usr/bin/env bash
# Bootstrap: devices NVIDIA + TF 2.15.1 (sm_75) + reset GPU se necessário + treino.
#   bash scripts/bootstrap_gpu_and_train.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONUNBUFFERED=1
export TF_CPP_MIN_LOG_LEVEL="${TF_CPP_MIN_LOG_LEVEL:-1}"
export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"
export TF_XLA_FLAGS="--tf_xla_auto_jit=0"
export TF_FORCE_GPU_ALLOW_GROWTH=true
# Evita misturar CUDA do sistema com as libs do wheel
unset LD_LIBRARY_PATH
unset CUDA_HOME
unset CUDA_PATH

echo "========================================"
echo " Bootstrap GPU + treino y_bilateral"
echo " $(date -Iseconds)"
echo "========================================"

if ! command -v uv >/dev/null 2>&1; then
  echo "ERRO: uv não encontrado." >&2
  exit 1
fi

PY="${ROOT}/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "ERRO: .venv não encontrado. Rode: uv sync" >&2
  exit 1
fi

echo ""
echo "=== 1/6 Reparar devices NVIDIA ==="
if ls /dev/nvidia0 >/dev/null 2>&1 && nvidia-smi >/dev/null 2>&1; then
  echo "OK: /dev/nvidia* e nvidia-smi já funcionam."
else
  echo "Solicitando sudo para criar /dev/nvidia* e instalar nvidia-modprobe..."
  sudo bash <<'ROOT'
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
if ! command -v nvidia-modprobe >/dev/null 2>&1; then
  apt-get update -qq
  apt-get install -y nvidia-modprobe
fi
nvidia-modprobe -u -c=0 || true
[[ -e /dev/nvidia0 ]] || mknod -m 666 /dev/nvidia0 c 195 0
[[ -e /dev/nvidiactl ]] || mknod -m 666 /dev/nvidiactl c 195 255
UVM_MAJOR=$(awk '/nvidia-uvm$/ {print $1}' /proc/devices | head -1)
UVM_MAJOR="${UVM_MAJOR:-507}"
[[ -e /dev/nvidia-uvm ]] || mknod -m 666 /dev/nvidia-uvm c "$UVM_MAJOR" 0
[[ -e /dev/nvidia-uvm-tools ]] || mknod -m 666 /dev/nvidia-uvm-tools c "$UVM_MAJOR" 1 || true
chmod 666 /dev/nvidia0 /dev/nvidiactl /dev/nvidia-uvm 2>/dev/null || true
nvidia-smi
ROOT
fi
nvidia-smi --query-gpu=name,driver_version,memory.free --format=csv

echo ""
echo "=== 2/6 Reset GPU (limpa estado após CUDA_ERROR_LAUNCH_FAILED) ==="
# Após abort/core dump o driver pode ficar em CUDA_ERROR_UNKNOWN até reset
if nvidia-smi >/dev/null 2>&1; then
  echo "Tentando nvidia-smi --gpu-reset (pode pedir sudo)..."
  if sudo -n nvidia-smi --gpu-reset -i 0 2>/dev/null; then
    echo "GPU reset OK (sudo -n)."
  else
    echo "Se o passo 5 falhar com CUDA_ERROR_UNKNOWN, rode:"
    echo "  sudo nvidia-smi --gpu-reset -i 0"
    echo "ou reinicie a sessão gráfica / o PC."
  fi
fi

echo ""
echo "=== 3/6 Sincronizar ambiente (tensorflow[and-cuda]==2.15.1) ==="
uv sync
TF_VER=$("$PY" -c 'import tensorflow as tf; print(tf.__version__)')
echo "TF instalado: $TF_VER"
if [[ "$TF_VER" != 2.15.* ]]; then
  echo "ERRO: esperava TensorFlow 2.15.x, obteve $TF_VER" >&2
  exit 1
fi

echo ""
echo "=== 4/6 LD_LIBRARY_PATH só com libs NVIDIA do venv ==="
NV_LIBS=$("$PY" - <<'PY'
from pathlib import Path
import site
# Ordem estável: runtime primeiro, depois o resto
priority = [
    "cuda_runtime", "cuda_nvrtc", "cublas", "cufft", "curand",
    "cusolver", "cusparse", "cudnn", "nccl", "cuda_cupti", "nvjitlink",
]
found = {}
for sp in site.getsitepackages():
    root = Path(sp) / "nvidia"
    if not root.is_dir():
        continue
    for d in root.iterdir():
        for sub in ("lib", "lib64"):
            p = d / sub
            if p.is_dir():
                found[d.name] = str(p)
paths = []
for name in priority:
    if name in found:
        paths.append(found.pop(name))
paths.extend(sorted(found.values()))
print(":".join(paths))
PY
)
export LD_LIBRARY_PATH="$NV_LIBS"
echo "LD_LIBRARY_PATH=${LD_LIBRARY_PATH:0:220}..."

echo ""
echo "=== 5/6 Validar GPU + sm_75 + conv ==="
validate_gpu() {
  "$PY" - <<'PY'
import tensorflow as tf
from tensorflow.python.platform import build_info as bi
caps = bi.build_info.get("cuda_compute_capabilities") or []
print("TF", tf.__version__)
print("cuda_caps", caps)
gpus = tf.config.list_physical_devices("GPU")
print("GPUs", gpus)
assert gpus, "TF sem GPU (cuInit falhou — tente: sudo nvidia-smi --gpu-reset -i 0)"
assert any("75" in str(c) for c in caps), f"Wheel sem sm_75: {caps}"
print("sm_75: OK")
with tf.device("/GPU:0"):
    x = tf.constant([1.0, 2.0])
    print("smoke:", tf.square(x).numpy())
    inp = tf.random.uniform((1, 32, 32, 3), dtype=tf.float32)
    k = tf.random.uniform((3, 3, 3, 8), dtype=tf.float32)
    out = tf.nn.conv2d(inp, k, strides=1, padding="SAME")
    print("conv smoke ok:", tuple(out.shape))
PY
}

if ! validate_gpu; then
  echo ""
  echo "Validação falhou. Pedindo reset da GPU com sudo..."
  sudo nvidia-smi --gpu-reset -i 0 || true
  sleep 2
  validate_gpu
fi
echo "GPU OK."

echo ""
echo "=== 6/6 Pré-processamento (resume) + treino y_bilateral ==="
"$PY" scripts/run_preprocessing_ablation.py --variant y_bilateral
"$PY" scripts/train_co2wounds_binary_from_zero.py \
  --data processed \
  --processed-variant y_bilateral \
  --require-gpu \
  --batch-size 1

echo ""
echo "=== Concluído: $(date -Iseconds) ==="
