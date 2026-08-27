#!/usr/bin/env bash

set -euo pipefail

ENV_FILE="/etc/aeroesp/aeroesp.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "Environment file not found."
    exit 1
fi

set -a
source "$ENV_FILE"
set +a

BACKUP_DIR="/var/backups/aeroesp"

mkdir -p "$BACKUP_DIR"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

export PGPASSWORD="$AEROESP_DB_PASSWORD"

pg_dump \
    --host="$AEROESP_DB_HOST" \
    --port="$AEROESP_DB_PORT" \
    --username="$AEROESP_DB_USER" \
    --format=custom \
    --file="$BACKUP_DIR/aeroesp_${TIMESTAMP}.dump" \
    "$AEROESP_DB_NAME"

unset PGPASSWORD

find "$BACKUP_DIR" \
    -type f \
    -name "aeroesp_*.dump" \
    -mtime +14 \
    -delete

echo "Backup completed."