#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" != "--confirm" || -z "${2:-}" ]]; then
  echo "Uso: scripts/restore.sh --confirm /caminho/do/backup"
  exit 2
fi

SOURCE="$(realpath "$2")"
test -f "${SOURCE}/database.dump"
test -f "${SOURCE}/objects.tar.gz"
(cd "$SOURCE" && sha256sum -c SHA256SUMS)

docker compose -f compose.prod.yaml stop api web
docker compose -f compose.prod.yaml exec -T db \
  dropdb -U "$POSTGRES_USER" --if-exists "$POSTGRES_DB"
docker compose -f compose.prod.yaml exec -T db \
  createdb -U "$POSTGRES_USER" "$POSTGRES_DB"
docker compose -f compose.prod.yaml exec -T db \
  pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists \
  <"${SOURCE}/database.dump"
docker compose -f compose.prod.yaml exec -T minio sh -c "rm -rf /data/* && tar -C /data -xzf -" \
  <"${SOURCE}/objects.tar.gz"
docker compose -f compose.prod.yaml up -d api web
echo "Restauração concluída a partir de ${SOURCE}"
