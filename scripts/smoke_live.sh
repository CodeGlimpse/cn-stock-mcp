#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

pytest -q tests/live -m "live and smoke" --maxfail=1 -rA
