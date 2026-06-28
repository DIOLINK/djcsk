#!/bin/bash
# ==============================================
# reset_db.sh — Resetea y regenera la base de datos de PupiStock
#
# Uso:
#   ./scripts/reset_db.sh          # backup + reset + seed + import
#   ./scripts/reset_db.sh --force  # igual pero actualiza productos existentes
#   ./scripts/reset_db.sh --only-backup  # solo hace backup, sin reset
#
# Ejecutar dentro del contenedor web o con el venv activo:
#   docker compose exec web sh scripts/reset_db.sh
# ==============================================
set -e

FORCE=""
ONLY_BACKUP=false

for arg in "$@"; do
    case $arg in
        --force) FORCE="--force" ;;
        --only-backup) ONLY_BACKUP=true ;;
    esac
done

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=========================================="
echo "  PupiStock — Reset de Base de Datos"
echo "  $(date)"
echo "=========================================="

# --- Paso 1: Backup de datos actuales ---
echo ""
echo "[1/4] Backup de datos actuales..."
mkdir -p backups
python manage.py dumpdata \
    --natural-foreign --natural-primary \
    -e contenttypes -e auth.Permission -e sessions \
    --indent 2 \
    > "backups/db_dump_${TIMESTAMP}.json" 2>/dev/null && \
    echo "  -> backups/db_dump_${TIMESTAMP}.json" || \
    echo "  [!] Advertencia: el backup puede estar vacío (DB sin datos)"

if $ONLY_BACKUP; then
    echo ""
    echo "Backup completado. No se modificó la base de datos."
    exit 0
fi

# --- Paso 2: Flush de la DB ---
echo ""
echo "[2/4] Limpiando base de datos..."
python manage.py flush --noinput
echo "  -> Base de datos vaciada."

# --- Paso 3: Migraciones, seed e importación ---
echo ""
echo "[3/4] Migrando y poblando..."
python manage.py migrate --noinput
echo "  -> Migraciones aplicadas."

python manage.py seed_categories
echo "  -> Categorías seed creadas."

python manage.py import_products $FORCE
echo "  -> Productos importados desde CSV."

# --- Paso 4: Superusuario ---
echo ""
echo "[4/4] Creando superusuario..."
python manage.py createsuperuser --noinput 2>/dev/null && \
    echo "  -> Superusuario creado." || \
    echo "  -> Superusuario omitido (ya existe o faltan variables SU_USERNAME, SU_PASSWORD, SU_EMAIL)."

echo ""
echo "=========================================="
echo "  Reset completado exitosamente."
echo "  Backup guardado en: backups/db_dump_${TIMESTAMP}.json"
echo "=========================================="
