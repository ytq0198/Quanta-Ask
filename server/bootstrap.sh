#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/mnt/localDisk3/weizian/Quanta-Ask"
test "$(id -un)" = "weizian"
case "$PROJECT_ROOT" in
  /mnt/localDisk3/weizian/*) ;;
  *) echo "Refusing unsafe project root: $PROJECT_ROOT" >&2; exit 2 ;;
esac

mkdir -p "$PROJECT_ROOT"
cd "$PROJECT_ROOT"
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[dev,model]'
.venv/bin/python -m pytest

