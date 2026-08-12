#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/mnt/localDisk3/weizian/Quanta-Ask"
VLLM_ENV="/mnt/localDisk3/weizian/conda_envs/vllm"
MODEL_PATH="/mnt/localDisk3/weizian/models/Qwen2.5-7B-Instruct"

test "$(id -un)" = "weizian"
case "$PROJECT_ROOT" in
  /mnt/localDisk3/weizian/*) ;;
  *) echo "Refusing unsafe project root: $PROJECT_ROOT" >&2; exit 2 ;;
esac

cd "$PROJECT_ROOT"
mkdir -p logs
export PATH="$VLLM_ENV/bin:$PATH"
export VLLM_USE_FLASHINFER_SAMPLER=0
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-1}"

exec "$VLLM_ENV/bin/python" -m vllm.entrypoints.openai.api_server \
  --model "$MODEL_PATH" \
  --served-model-name qwen2.5-7b-instruct \
  --host 127.0.0.1 \
  --port "${QUANTA_ASK_VLLM_PORT:-8012}" \
  --dtype half \
  --gpu-memory-utilization "${QUANTA_ASK_GPU_MEMORY_UTILIZATION:-0.65}" \
  --max-model-len 4096 \
  --enforce-eager
