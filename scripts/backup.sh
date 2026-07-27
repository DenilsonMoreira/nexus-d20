#!/usr/bin/env bash
set -euo pipefail

BACKUP_ROOT="${BACKUP_ROOT:-/var/backups/nexus-d20}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TARGET="${BACKUP_ROOT}/${STAMP}"
mkdir -p "$TARGET"

docker compose -f compose.prod.yaml exec -T db \
  pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc >"${TARGET}/database.dump"
docker compose -f compose.prod.yaml exec -T minio \
  sh -c "tar -C /data -czf - ." >"${TARGET}/objects.tar.gz"
sha256sum "${TARGET}/database.dump" "${TARGET}/objects.tar.gz" >"${TARGET}/SHA256SUMS"

find "$BACKUP_ROOT" -mindepth 1 -maxdepth 1 -type d -mtime +"${BACKUP_RETENTION_DAYS:-30}" \
  -print -exec rm -rf -- {} +
echo "Backup criado em ${TARGET}"
