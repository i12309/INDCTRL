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

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 path/to/backup.sql.gz" >&2
  exit 1
fi

BACKUP_FILE="$1"
POSTGRES_DB="${POSTGRES_DB:-indctrl}"
POSTGRES_USER="${POSTGRES_USER:-indctrl}"

if [ ! -f "${BACKUP_FILE}" ]; then
  echo "Backup file not found: ${BACKUP_FILE}" >&2
  exit 1
fi

echo "WARNING: restore will write data into PostgreSQL database '${POSTGRES_DB}'."
echo "Stop application services before restore:"
echo "  docker compose stop indctrl"
echo
read -r -p "Type RESTORE to continue: " CONFIRMATION

if [ "${CONFIRMATION}" != "RESTORE" ]; then
  echo "Restore cancelled"
  exit 1
fi

echo "Restoring backup: ${BACKUP_FILE}"

if [[ "${BACKUP_FILE}" == *.gz ]]; then
  gzip -dc "${BACKUP_FILE}" | docker compose exec -T postgres psql \
    -U "${POSTGRES_USER}" \
    -d "${POSTGRES_DB}"
else
  docker compose exec -T postgres psql \
    -U "${POSTGRES_USER}" \
    -d "${POSTGRES_DB}" \
    < "${BACKUP_FILE}"
fi

echo "Restore finished"
echo "Start application services:"
echo "  docker compose up -d indctrl"
