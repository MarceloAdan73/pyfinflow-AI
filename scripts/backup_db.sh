#!/bin/bash
# PyFinFlow-AI - PostgreSQL Backup Script
# Usage: ./scripts/backup_db.sh [output_dir]
# Requires: pg_dump (PostgreSQL client), environment variables set

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Load .env if available
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
fi

: "${DATABASE_URL:=postgresql://postgres:postgres@localhost:5432/pyfinflow_dev}"
: "${BACKUP_DIR:=${1:-$PROJECT_DIR/backups}}"
: "${RETENTION_DAYS:=7}"

mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/pyfinflow_$TIMESTAMP.sql"
BACKUP_GZ="$BACKUP_FILE.gz"

echo "=== PyFinFlow Backup ==="
echo "Database: $DATABASE_URL"
echo "Output: $BACKUP_GZ"
echo ""

# Extract parts from DATABASE_URL
if [[ "$DATABASE_URL" =~ postgresql://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+) ]]; then
    DB_USER="${BASH_REMATCH[1]}"
    DB_PASS="${BASH_REMATCH[2]}"
    DB_HOST="${BASH_REMATCH[3]}"
    DB_PORT="${BASH_REMATCH[4]}"
    DB_NAME="${BASH_REMATCH[5]}"
else
    echo "ERROR: Could not parse DATABASE_URL"
    exit 1
fi

export PGPASSWORD="$DB_PASS"

echo "Running pg_dump..."
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    --format=custom \
    --verbose \
    --file="$BACKUP_FILE" 2>&1

echo "Compressing..."
gzip -f "$BACKUP_FILE"

echo ""
echo "Backup complete: $BACKUP_GZ"
echo "Size: $(ls -lh "$BACKUP_GZ" | awk '{print $5}')"

# Cleanup old backups
echo ""
echo "Cleaning backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "pyfinflow_*.sql.gz" -mtime "+$RETENTION_DAYS" -delete
find "$BACKUP_DIR" -name "pyfinflow_*.sql" -mtime "+$RETENTION_DAYS" -delete

echo "Done."
