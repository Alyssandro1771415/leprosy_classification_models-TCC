#!/bin/bash
set -e
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y nvidia-modprobe
nvidia-modprobe -u -c=0 || true
[[ -e /dev/nvidia0 ]] || mknod -m 666 /dev/nvidia0 c 195 0
[[ -e /dev/nvidiactl ]] || mknod -m 666 /dev/nvidiactl c 195 255
UVM_MAJOR=$(awk '/nvidia-uvm$/ {print $1}' /proc/devices | head -1)
UVM_MAJOR="${UVM_MAJOR:-507}"
[[ -e /dev/nvidia-uvm ]] || mknod -m 666 /dev/nvidia-uvm c "$UVM_MAJOR" 0
[[ -e /dev/nvidia-uvm-tools ]] || mknod -m 666 /dev/nvidia-uvm-tools c "$UVM_MAJOR" 1 || true
ls -la /dev/nvidia*
nvidia-smi
