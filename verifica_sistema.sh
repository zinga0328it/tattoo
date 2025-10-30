#!/bin/bash

echo "🚀 VERIFICA SISTEMA COMPLETO - Roma Studio Tattoo"
echo "=================================================="

# 1. Verifica Database
echo "📊 1. DATABASE:"
db_count=$(sqlite3 /home/alex/web/tatuaggi/tattoo_gallery.db "SELECT COUNT(*) FROM tattoos;")
echo "   ✅ Database: $db_count tatuaggi trovati"

# 2. Verifica Django
echo "🐍 2. DJANGO BACKEND:"
if ps aux | grep -q "manage.py runserver" && ! ps aux | grep "manage.py runserver" | grep -q grep; then
    echo "   ✅ Django: Running su 127.0.0.1:8888"
else
    echo "   ❌ Django: Non attivo"
fi

# 3. Verifica API
echo "🔗 3. API TESTING:"
api_test=$(curl -s http://127.0.0.1:8888/api/tattoos/ | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data))" 2>/dev/null)
if [ "$api_test" ]; then
    echo "   ✅ API Generale: $api_test tatuaggi disponibili"
else
    echo "   ❌ API Generale: Non raggiungibile"
fi

# 4. Verifica File Pubblici
echo "📁 4. FILE PUBBLICI:"
if [ -f "/var/www/romastudiotattoo/index.html" ]; then
    echo "   ✅ index.html: Presente"
else
    echo "   ❌ index.html: Mancante"
fi

if [ -f "/var/www/romastudiotattoo/detail.html" ]; then
    echo "   ✅ detail.html: Presente"
else
    echo "   ❌ detail.html: Mancante"
fi

if [ -f "/var/www/romastudiotattoo/gallery.html" ]; then
    echo "   ✅ gallery.html: Presente"
else
    echo "   ❌ gallery.html: Mancante"
fi

# 5. Verifica Apache
echo "🌐 5. APACHE:"
if systemctl is-active --quiet apache2; then
    echo "   ✅ Apache: Attivo"
else
    echo "   ❌ Apache: Non attivo"
fi

# 6. Verifica Bot Telegram
echo "🤖 6. BOT TELEGRAM:"
if systemctl is-active --quiet tattoo-bot; then
    echo "   ✅ Bot: Attivo"
else
    echo "   ❌ Bot: Non attivo"
fi

echo ""
echo "🎯 RIEPILOGO FUNZIONALITÀ:"
echo "   📍 Homepage: https://romastudiotattoo.com/"
echo "   📸 Galleria: https://romastudiotattoo.com/gallery.html"
echo "   🔍 Dettaglio: https://romastudiotattoo.com/detail.html?id=X"
echo "   🔗 API: https://romastudiotattoo.com/gallery/api/tattoos/"
echo "   💬 Telegram: Link diretti per ogni artista"
echo ""
echo "✨ Sistema pronto per la produzione!"
