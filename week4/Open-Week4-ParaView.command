#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA="$ROOT/week4/results/guard_ring_gap3_h0.025/structure.vtu"

if [[ ! -f "$DATA" ]]; then
  echo "Run '.venv/bin/python week4/guard_ring.py mesh' first."
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
