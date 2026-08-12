#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/mnt/localDisk3/weizian/Quanta-Ask"
VLLM_ENV="/mnt/localDisk3/weizian/conda_envs/vllm"

test "$(id -un)" = "weizian"
case "$PROJECT_ROOT" in
  /mnt/localDisk3/weizian/*) ;;
  *) echo "Refusing unsafe project root: $PROJECT_ROOT" >&2; exit 2 ;;
esac

: "${QUANTA_ASK_MODEL_PATH:?Set QUANTA_ASK_MODEL_PATH}"
: "${QUANTA_ASK_SERVED_MODEL_NAME:?Set QUANTA_ASK_SERVED_MODEL_NAME}"

case "$QUANTA_ASK_MODEL_PATH" in
  /mnt/localDisk3/weizian/*) ;;
  *) echo "Refusing model outside the authorized tree: $QUANTA_ASK_MODEL_PATH" >&2; exit 2 ;;
esac
test -d "$QUANTA_ASK_MODEL_PATH"

cd "$PROJECT_ROOT"
mkdir -p logs
export PATH="$VLLM_ENV/bin:$PATH"
export VLLM_USE_FLASHINFER_SAMPLER=0
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-1}"

exec "$VLLM_ENV/bin/python" -m vllm.entrypoints.openai.api_server \
  --model "$QUANTA_ASK_MODEL_PATH" \
  --served-model-name "$QUANTA_ASK_SERVED_MODEL_NAME" \
  --host 127.0.0.1 \
  --port "${QUANTA_ASK_VLLM_PORT:-8012}" \
  --dtype "${QUANTA_ASK_DTYPE:-half}" \
  --gpu-memory-utilization "${QUANTA_ASK_GPU_MEMORY_UTILIZATION:-0.65}" \
  --max-model-len "${QUANTA_ASK_MAX_MODEL_LEN:-4096}" \
  --generation-config vllm \
  --enforce-eager
