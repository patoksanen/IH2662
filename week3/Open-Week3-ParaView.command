#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA="$ROOT/week3/results/baseline_double_h1/final.vtu"

if [[ ! -f "$DATA" ]]; then
  echo "Run '.venv/bin/python week3/silicon_baseline.py run' first."
  exit 1
fi

for APP in \
  "$HOME/Applications/ParaView-6.1.1.app/Contents/MacOS/paraview" \
  "/Applications/ParaView-6.1.1.app/Contents/MacOS/paraview"; do
  if [[ -x "$APP" ]]; then
    exec "$APP" --data="$DATA"
  fi
done

if command -v paraview >/dev/null 2>&1; then
  exec paraview --data="$DATA"
fi

echo "ParaView was not found. Install it with: brew install --cask paraview"
exit 1
