#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
mkdir -p "${BACKUP_DIR}"

docker compose exec -T postgres pg_dump \
  -U "${POSTGRES_USER:-machine_control}" \
  -d "${POSTGRES_DB:-machine_control}" \
  > "${BACKUP_DIR}/postgres_${TIMESTAMP}.sql"
