#!/bin/bash
# Script que espera a que ngrok levante y muestra la URL pública apenas esté disponible

# Máximo 60 intentos (30 segundos)
MAX_TRIES=60
TRIES=0

while [ $TRIES -lt $MAX_TRIES ]; do
    URL=$(docker-compose logs ngrok 2>/dev/null | grep -Eo 'https://[a-zA-Z0-9\-]+\.ngrok-free\.app' | tail -1)
    if [ -n "$URL" ]; then
        echo "ngrok URL: $URL"
        exit 0
    fi
    TRIES=$((TRIES+1))
    sleep 0.5
done

echo "No se detectó una URL de ngrok tras $((MAX_TRIES/2)) segundos." >&2
exit 1
