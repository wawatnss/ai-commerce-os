#!/bin/bash
# Backup AI Commerce OS data
# Usage: ./backup.sh [backup_dir]

set -e

BACKUP_DIR=${1:-"./backups"}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

# Database
docker exec ai-commerce-postgres pg_dump -U ai_commerce ai_commerce > "$BACKUP_DIR/ai_commerce_db_$TIMESTAMP.sql"

# Redis (RDB is already persisted; copy dump.rdb if available)
docker cp ai-commerce-redis:/data/dump.rdb "$BACKUP_DIR/redis_dump_$TIMESTAMP.rdb" || true

# Validation reports
if [ -d "../validation" ]; then
  tar -czf "$BACKUP_DIR/validation_$TIMESTAMP.tar.gz" -C ".." validation || true
fi

echo "Backup created in $BACKUP_DIR for timestamp $TIMESTAMP"
