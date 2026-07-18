#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Arquivo .env criado. Revise os segredos antes de publicar."
fi

docker compose up --build -d
docker compose run --rm api alembic upgrade head

echo "Nexus d20 iniciado em http://localhost:3000"
