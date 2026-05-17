#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 path/to/backup.sql" >&2
  exit 1
fi

docker compose exec -T postgres psql \
  -U "${POSTGRES_USER:-machine_control}" \
  -d "${POSTGRES_DB:-machine_control}" \
  < "$1"
