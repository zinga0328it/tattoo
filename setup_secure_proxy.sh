#!/bin/bash

# SCRIPT SICUREZZA DJANGO + APACHE PROXY
echo "🔒 CONFIGURAZIONE SICURA DJANGO + APACHE"

# 1. Backup del config Apache
sudo cp /etc/apache2/sites-enabled/romastudiotattoo-ssl.conf /etc/apache2/sites-enabled/romastudiotattoo-ssl.conf.backup

# 2. Aggiunge il proxy SICURO
sudo sed -i '/SSLCertificateKeyFile/a\
\
    # PROXY SICURO PER DJANGO GALLERY\
    ProxyPass /gallery/ http://127.0.0.1:8888/\
    ProxyPassReverse /gallery/ http://127.0.0.1:8888/\
    ProxyPreserveHost On\
\
    # HEADERS DI SICUREZZA\
    Header always set X-Frame-Options DENY\
    Header always set X-Content-Type-Options nosniff\
    Header always set X-XSS-Protection "1; mode=block"\
\
    # BLOCCA ACCESSO DIRETTO A DJANGO\
    <Location "/gallery/">\
        Require local\
    </Location>' /etc/apache2/sites-enabled/romastudiotattoo-ssl.conf

echo "✅ Configurazione Apache completata"

# 3. Configura Django per produzione SICURA
cd /home/alex/web/tatuaggi/tattoo_gallery

# Settings di produzione
cat >> tattoo_gallery/settings.py << 'EOF'

# CONFIGURAZIONE SICURA PRODUZIONE
DEBUG = False
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'romastudiotattoo.com', 'www.romastudiotattoo.com']

# URL ROOT per il proxy
FORCE_SCRIPT_NAME = '/gallery'
STATIC_URL = '/gallery/static/'

# SICUREZZA
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
EOF

echo "✅ Django configurato per produzione SICURA"

# 4. Reload Apache
sudo systemctl reload apache2

echo "🚀 TUTTO PRONTO! Django è accessibile solo tramite Apache proxy SICURO"
echo "📍 URL: https://romastudiotattoo.com/gallery/"
