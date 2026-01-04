#!/bin/bash

echo "🔄 RIAVVIO SISTEMA ROMA STUDIO TATTOO"
echo "====================================="
echo

# Colori per l'output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "⏹️  Fermando tutti i servizi..."
sudo systemctl stop tattoo-system
sudo systemctl stop tattoo-bot
sudo systemctl stop django-gallery

echo "⏳ Aspetto 3 secondi..."
sleep 3

echo "🚀 Riavviando i servizi..."
sudo systemctl start tattoo-system

echo "⏳ Aspetto che i servizi si avviino..."
sleep 10

echo "📊 Controllo stato finale:"
echo "========================="

./check_system.sh
