#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PYTHON="${PYTHON:-python3}"
VENV="$ROOT/.venv"

if [[ ! -x "$VENV/bin/python" ]]; then
  "$PYTHON" -m venv "$VENV"
fi

"$VENV/bin/python" -m pip install --upgrade pip
if [[ "$(uname -s)" == "Darwin" ]]; then
  "$VENV/bin/python" -m pip install -r "$ROOT/requirements-macos.txt"
else
  "$VENV/bin/python" -m pip install -r "$ROOT/requirements-lock.txt"
fi

"$VENV/bin/python" -m pip check
"$VENV/bin/python" "$ROOT/check_setup.py"
echo "PASS: IH2662 simulation environment is ready."
