#!/bin/bash

echo "🚀 DEPLOY AUTOMATICO - Roma Studio Tattoo"
echo "========================================"

# Directory di origine (sviluppo)
SRC_DIR="/home/alex/web/tatuaggi/tattoo_gallery/test_romastudiotattoo"
# Directory di destinazione (produzione)
DEST_DIR="/var/www/romastudiotattoo"

echo "📂 Directory origine: $SRC_DIR"
echo "📂 Directory destinazione: $DEST_DIR"

# 1. Backup della directory pubblica
echo "💾 1. Creazione backup..."
sudo cp -r $DEST_DIR ${DEST_DIR}_backup_$(date +%Y%m%d_%H%M%S)

# 2. Copia file HTML aggiornati
echo "📄 2. Deploy file HTML..."
sudo cp $SRC_DIR/index.html $DEST_DIR/
echo "   ✅ index.html copiato"

sudo cp $SRC_DIR/gallery.html $DEST_DIR/
echo "   ✅ gallery.html copiato"

sudo cp $SRC_DIR/detail.html $DEST_DIR/
echo "   ✅ detail.html copiato"

# 3. Copia JavaScript se presente
if [ -f "$SRC_DIR/gallery-django.js" ]; then
    sudo cp $SRC_DIR/gallery-django.js $DEST_DIR/
    echo "   ✅ gallery-django.js copiato"
fi

# 4. Verifica permessi
echo "🔐 3. Verifica permessi..."
sudo chown -R www-data:www-data $DEST_DIR
sudo chmod -R 644 $DEST_DIR/*
sudo chmod 755 $DEST_DIR/images

# 5. Test sistema
echo "🧪 4. Test sistema..."

# Verifica Django attivo
if ps aux | grep -q "manage.py runserver" && ! ps aux | grep "manage.py runserver" | grep -q grep; then
    echo "   ✅ Django Backend: ATTIVO"
else
    echo "   ❌ Django Backend: NON ATTIVO"
    echo "   🔧 Avviando Django..."
    cd /home/alex/web/tatuaggi/tattoo_gallery
    python3 manage.py runserver 127.0.0.1:8888 &
    sleep 3
fi

# Test API
echo "   🔗 Test API..."
api_response=$(curl -s http://127.0.0.1:8888/api/tattoos/ | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data))" 2>/dev/null)
if [ "$api_response" ]; then
    echo "   ✅ API Response: $api_response tatuaggi"
else
    echo "   ❌ API non raggiungibile"
fi

# 6. Test finale su produzione
echo "🌐 5. Test finale produzione..."
if curl -s https://romastudiotattoo.com/ | grep -q "galleria"; then
    echo "   ✅ Homepage: ONLINE"
else
    echo "   ❌ Homepage: ERRORE"
fi

if curl -s https://romastudiotattoo.com/gallery/api/tattoos/ | grep -q '\['; then
    echo "   ✅ API Produzione: ONLINE"
else
    echo "   ❌ API Produzione: ERRORE"
fi

echo ""
echo "🎉 DEPLOY COMPLETATO!"
echo "📍 URL da testare:"
echo "   🏠 Homepage: https://romastudiotattoo.com/"
echo "   📸 Galleria: https://romastudiotattoo.com/gallery.html" 
echo "   🔍 Dettaglio: https://romastudiotattoo.com/detail.html?id=1"
echo "   🔗 API: https://romastudiotattoo.com/gallery/api/tattoos/"
echo ""
echo "✨ Sistema pronto per la produzione!"
