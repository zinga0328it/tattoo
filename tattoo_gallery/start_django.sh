#!/bin/bash
# Script di avvio per Django Tattoo Gallery

# Vai nella directory corretta
cd /home/alex/web/tatuaggi/tattoo_gallery || { echo "Impossibile accedere alla directory /home/alex/web/tatuaggi/tattoo_gallery"; exit 1; }

# Imposta le variabili d'ambiente
export PYTHONPATH=/home/alex/web/tatuaggi/tattoo_gallery
export DJANGO_SETTINGS_MODULE=tattoo_gallery.settings
export PATH=/home/alex/.local/bin:$PATH

# Verifica che gunicorn esista
if ! command -v gunicorn &> /dev/null; then
    echo "Gunicorn non trovato"
    exit 1
fi

# Avvia gunicorn
exec /home/alex/.local/bin/gunicorn --bind 127.0.0.1:8888 tattoo_gallery.wsgi:application
