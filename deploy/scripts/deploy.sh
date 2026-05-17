#!/usr/bin/env bash
set -euo pipefail

docker compose -f compose.production.yml build
docker compose -f compose.production.yml up -d
docker compose -f compose.production.yml ps
