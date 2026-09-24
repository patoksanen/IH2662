#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec "$ROOT/ih2662.sh" "$ROOT/week4/guard_ring.py" "$@"
