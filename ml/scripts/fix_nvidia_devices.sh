#!/usr/bin/env bash
# Repara nodes /dev/nvidia* (comuns após reboot sem nvidia-modprobe) e testa TF+GPU.
set -euo pipefail

echo "=== 1) Estado atual ==="
ls -la /dev/nvidia* 2>&1 || true
nvidia-smi --query-gpu=name,memory.free --format=csv 2>&1 || true

if ! ls /dev/nvidia0 >/dev/null 2>&1; then
  echo ""
  echo "=== 2) Criando /dev/nvidia* (precisa sudo) ==="
  if ! command -v nvidia-modprobe >/dev/null 2>&1; then
    echo "Instalando nvidia-modprobe..."
    sudo apt-get update -qq
    sudo apt-get install -y nvidia-modprobe
  fi
  sudo nvidia-modprobe -u -c=0 || true
  # Fallback manual se modprobe não criar tudo
  if [[ ! -e /dev/nvidia0 ]]; then
    sudo mknod -m 666 /dev/nvidia0 c 195 0
  fi
  if [[ ! -e /dev/nvidiactl ]]; then
    sudo mknod -m 666 /dev/nvidiactl c 195 255
  fi
  # major do uvm (ver /proc/devices)
  UVM_MAJOR=$(awk '/nvidia-uvm$/ {print $1}' /proc/devices | head -1)
  UVM_MAJOR="${UVM_MAJOR:-507}"
  if [[ ! -e /dev/nvidia-uvm ]]; then
    sudo mknod -m 666 /dev/nvidia-uvm c "$UVM_MAJOR" 0
  fi
  if [[ ! -e /dev/nvidia-uvm-tools ]]; then
    sudo mknod -m 666 /dev/nvidia-uvm-tools c "$UVM_MAJOR" 1 || true
  fi
fi

echo ""
echo "=== 3) nvidia-smi ==="
ls -la /dev/nvidia*
nvidia-smi

echo ""
echo "=== 4) TensorFlow GPU ==="
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
unset LD_LIBRARY_PATH
export TF_CPP_MIN_LOG_LEVEL=0
if command -v uv >/dev/null 2>&1; then
  uv run python -u -c 'import tensorflow as tf; print("TF", tf.__version__); print(tf.config.list_physical_devices("GPU"))'
else
  .venv/bin/python -u -c 'import tensorflow as tf; print("TF", tf.__version__); print(tf.config.list_physical_devices("GPU"))'
fi
