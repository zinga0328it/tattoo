#!/bin/bash

echo "🚀 CONTROLLO SISTEMA ROMA STUDIO TATTOO"
echo "======================================="
echo

# Colori per l'output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funzione per controllare lo stato di un servizio
check_service() {
    local service=$1
    local name=$2
    
    if systemctl is-active --quiet $service; then
        echo -e "✅ $name: ${GREEN}ATTIVO${NC}"
        return 0
    else
        echo -e "❌ $name: ${RED}INATTIVO${NC}"
        return 1
    fi
}

# Funzione per controllare se un servizio è abilitato
check_enabled() {
    local service=$1
    local name=$2
    
    if systemctl is-enabled --quiet $service; then
        echo -e "🔄 $name: ${GREEN}ABILITATO per l'avvio automatico${NC}"
        return 0
    else
        echo -e "⚠️  $name: ${YELLOW}NON ABILITATO per l'avvio automatico${NC}"
        return 1
    fi
}

# Controllo servizi
echo "📊 STATO SERVIZI:"
echo "----------------"
all_services_ok=true

if ! check_service apache2 "Apache Web Server"; then
    all_services_ok=false
fi

if ! check_service django-gallery "Django API"; then
    all_services_ok=false
fi

if ! check_service tattoo-bot "Telegram Bot"; then
    all_services_ok=false
fi

if ! check_service tattoo-system "Sistema Completo"; then
    all_services_ok=false
fi

echo
echo "🔄 AVVIO AUTOMATICO:"
echo "-------------------"
check_enabled apache2 "Apache Web Server"
check_enabled django-gallery "Django API"  
check_enabled tattoo-bot "Telegram Bot"
check_enabled tattoo-system "Sistema Completo"

echo
echo "🌐 TEST CONNETTIVITÀ:"
echo "--------------------"

# Test Django API
if curl -s http://127.0.0.1:8888/api/tattoos/ > /dev/null; then
    echo -e "✅ Django API: ${GREEN}RISPONDE${NC}"
else
    echo -e "❌ Django API: ${RED}NON RISPONDE${NC}"
    all_services_ok=false
fi

# Test sito web
if curl -s https://www.romastudiotattoo.it > /dev/null; then
    echo -e "✅ Sito Web: ${GREEN}ACCESSIBILE${NC}"
else
    echo -e "❌ Sito Web: ${RED}NON ACCESSIBILE${NC}"
    all_services_ok=false
fi

echo
echo "📂 CONTROLLO FILES:"
echo "------------------"

# Controllo database
if [ -f "/home/alex/web/tatuaggi/tattoo_gallery.db" ]; then
    tattoo_count=$(sqlite3 /home/alex/web/tatuaggi/tattoo_gallery.db "SELECT COUNT(*) FROM tattoos;" 2>/dev/null || echo "ERROR")
    if [ "$tattoo_count" != "ERROR" ]; then
        echo -e "✅ Database: ${GREEN}OK${NC} ($tattoo_count tatuaggi)"
    else
        echo -e "❌ Database: ${RED}ERRORE DI LETTURA${NC}"
    fi
else
    echo -e "❌ Database: ${RED}FILE NON TROVATO${NC}"
    all_services_ok=false
fi

# Controllo directory immagini
if [ -d "/var/www/romastudiotattoo/images" ]; then
    image_count=$(ls -1 /var/www/romastudiotattoo/images/*.jpg 2>/dev/null | wc -l)
    echo -e "✅ Directory Immagini: ${GREEN}OK${NC} ($image_count immagini)"
else
    echo -e "❌ Directory Immagini: ${RED}NON TROVATA${NC}"
    all_services_ok=false
fi

echo
echo "======================================="
if [ "$all_services_ok" = true ]; then
    echo -e "🎉 ${GREEN}TUTTO FUNZIONA CORRETTAMENTE!${NC}"
    echo -e "🚀 ${GREEN}Il sistema partirà automaticamente al riavvio${NC}"
else
    echo -e "⚠️  ${YELLOW}ALCUNI PROBLEMI RILEVATI${NC}"
    echo "Controlla i servizi sopra indicati"
fi
echo "======================================="
