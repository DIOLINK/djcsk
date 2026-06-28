#!/bin/bash
# ==============================================
# dump_db.sh — Backup rápido de los datos
#
# Uso:
#   ./scripts/dump_db.sh
#   docker compose exec web sh scripts/dump_db.sh
# ==============================================
set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p backups

echo "[dump_db] Exportando datos..."
python manage.py dumpdata \
    --natural-foreign --natural-primary \
    -e contenttypes -e auth.Permission -e sessions \
    --indent 2 \
    > "backups/db_dump_${TIMESTAMP}.json" 2>/dev/null

FILESIZE=$(wc -c < "backups/db_dump_${TIMESTAMP}.json" 2>/dev/null || echo 0)
echo "[dump_db] backups/db_dump_${TIMESTAMP}.json (${FILESIZE} bytes)"
