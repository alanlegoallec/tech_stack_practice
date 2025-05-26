#!/bin/bash
# filepath: db/init-rds.sh

set -e

# Source environment variables from .env in project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$SCRIPT_DIR/.."
if [ -f "$ROOT_DIR/.env" ]; then
  set -a
  source "$ROOT_DIR/.env"
  set +a
else
  echo ".env file not found in $ROOT_DIR"
  exit 1
fi

psql -h "$RDS_DB_HOST" -p "$RDS_DB_PORT" -U "$RDS_DB_USER" -d "$RDS_DB_NAME" -f db/init.sql
