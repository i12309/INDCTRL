#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  source ".env"
  set +a
fi

POSTGRES_DB="${POSTGRES_DB:-indctrl}"
POSTGRES_USER="${POSTGRES_USER:-indctrl}"
BACKUP_DIR="${BACKUP_DIR:-./backups/postgres}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
TIMESTAMP="$(date +%Y-%m-%d_%H%M%S)"
BACKUP_FILE="${BACKUP_DIR}/${POSTGRES_DB}_${TIMESTAMP}.sql.gz"

echo "INDCTRL PostgreSQL backup started"
echo "Database: ${POSTGRES_DB}"
echo "Backup file: ${BACKUP_FILE}"

mkdir -p "${BACKUP_DIR}"

docker compose exec -T postgres pg_dump \
  -U "${POSTGRES_USER}" \
  -d "${POSTGRES_DB}" \
  | gzip > "${BACKUP_FILE}"

if [ ! -s "${BACKUP_FILE}" ]; then
  echo "Backup failed: file is empty" >&2
  exit 1
fi

echo "Backup created: ${BACKUP_FILE}"
echo "Removing backups older than ${BACKUP_RETENTION_DAYS} days"

find "${BACKUP_DIR}" \
  -type f \
  -name "${POSTGRES_DB}_*.sql.gz" \
  -mtime +"${BACKUP_RETENTION_DAYS}" \
  -print \
  -delete

echo "INDCTRL PostgreSQL backup finished"
