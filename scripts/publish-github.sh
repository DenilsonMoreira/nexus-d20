#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${1:-}"
if [[ -z "$REPO_URL" ]]; then
  echo "Uso: ./scripts/publish-github.sh git@github.com:USUARIO/nexus-d20.git"
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git init -b main
fi

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REPO_URL"
else
  git remote add origin "$REPO_URL"
fi

git add -A
if ! git diff --cached --quiet; then
  git commit -m "chore: initialize Nexus d20"
fi

git push -u origin main
