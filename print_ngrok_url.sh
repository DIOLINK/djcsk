#!/bin/bash
# Script para imprimir solo la URL pública de ngrok (sidecar docker)
# Debe ejecutarse en la raíz del proyecto Docker Compose

docker-compose logs ngrok 2>/dev/null | grep -Eo 'https://[a-zA-Z0-9\-]+\.ngrok-free\.app' | tail -1
