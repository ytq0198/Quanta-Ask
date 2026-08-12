#!/usr/bin/env bash
set -euo pipefail

export QUANTA_ASK_MODEL_PATH="/mnt/localDisk3/weizian/models/Qwen2.5-7B-Instruct"
export QUANTA_ASK_SERVED_MODEL_NAME="qwen2.5-7b-instruct"
exec /mnt/localDisk3/weizian/Quanta-Ask/server/run_vllm_model.sh
