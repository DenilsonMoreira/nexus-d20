#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -d "$ROOT/backend/.venv" ]]; then
  source "$ROOT/backend/.venv/bin/activate"
fi

(
  cd "$ROOT/backend"
  ruff check app tests migrations
  mypy app
  pytest
)

(
  cd "$ROOT/frontend"
  npm run lint
  npm run typecheck
  npm test
  npm run build
)
