# 🎨 Roma Studio Tattoo - Galleria Digitale

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://www.djangoproject.com/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://telegram.org/)

> **Sistema completo per la gestione digitale di gallerie tattoo con bot Telegram integrato**

Roma Studio Tattoo è una piattaforma innovativa che rivoluziona il modo in cui tatuatori e clienti interagiscono. Combina un backend Django sicuro con un bot Telegram intelligente per creare una galleria dinamica e interattiva.

## 🌟 Caratteristiche Principali

### 🤖 Bot Telegram Intelligente
- **Caricamento Semplificato**: I tatuatori caricano le loro opere direttamente via Telegram
- **Elaborazione Automatica**: Immagini ottimizzate e catalogate automaticamente
- **Notifiche Real-time**: Aggiornamenti istantanei della galleria

### 🔒 Sicurezza Enterprise
- **Architettura Isolata**: Django backend protetto su localhost
- **Proxy Apache Sicuro**: Comunicazione tramite reverse proxy con headers di sicurezza
- **File Statici Separati**: Nessun codice Python accessibile dal web pubblico

### 🎯 Funzionalità Avanzate
- **SEO Ottimizzato**: Meta tag dinamici per ogni tatuaggio
- **Contatti Diretti**: Link Telegram per comunicazione immediata artista-cliente
- **Sistema Like**: Interazione social con localStorage
- **Galleria Responsive**: Design moderno e adattivo

### 📊 Dashboard Amministrativa
- **Gestione Database**: Interfaccia Django completa
- **Statistiche Real-time**: Monitoraggio caricamenti e visualizzazioni
- **Backup Automatici**: Sistema di salvataggio sicuro

## 🏗️ Architettura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram Bot  │───▶│   Django API    │───▶│   Database      │
│   (Upload)      │    │   (Processing)  │    │   (SQLite)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Apache Proxy   │───▶│ Static Files    │───▶│   Web Gallery   │
│  (Security)     │    │ (HTML/CSS/JS)   │    │   (Public)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Installazione e Setup

### Prerequisiti
- Python 3.10+
- Django 4.2+
- Apache 2.4+
- Telegram Bot Token

### 1. Clona il Repository
```bash
git clone https://github.com/zinga0328it/tattoo.git
cd tattoo
```

### 2. Installa Dipendenze
```bash
pip install -r requirements.txt
```

### 3. Configurazione Database
```bash
cd tattoo_gallery
python manage.py migrate
python manage.py createsuperuser
```

### 4. Configurazione Bot Telegram
```bash
# Modifica bot.py con il tuo BOT_TOKEN
nano bot.py
```

### 5. Avvia i Servizi
```bash
# Backend Django
sudo systemctl start django-gallery

# Bot Telegram
sudo systemctl start tattoo-bot

# Apache Proxy
sudo systemctl restart apache2
```

## 📖 Come Usare

### Per Tatuatori
1. **Contatta il Bot**: Inizia una chat con `@provatel_bot` su Telegram
2. **Carica Foto**: Invia le tue opere d'arte
3. **Aggiungi Descrizioni**: Fornisci dettagli sui tuoi tatuaggi
4. **Pubblicazione Automatica**: Le tue opere appaiono nella galleria

### Per Clienti
1. **Esplora Galleria**: Visita `https://romastudiotattoo.com/gallery.html`
2. **Scopri Artisti**: Clicca sui tatuaggi per vedere i dettagli
3. **Contatta Artisti**: Usa i link Telegram per prenotazioni
4. **Salva Preferiti**: Sistema like integrato

## 🔧 Configurazioni

### Apache Proxy Configuration
```apache
<VirtualHost *:443>
    ServerName romastudiotattoo.com
    
    # File statici pubblici
    DocumentRoot /var/www/romastudiotattoo
    
    # Proxy per Django API
    ProxyPass /gallery/api http://127.0.0.1:8888/gallery/api
    ProxyPassReverse /gallery/api http://127.0.0.1:8888/gallery/api
    
    # Sicurezza
    <Location /gallery/api>
        Require all granted
        Header always set X-Frame-Options DENY
        Header always set X-Content-Type-Options nosniff
    </Location>
</VirtualHost>
```

### Environment Variables
```bash
# .env file
DJANGO_SECRET_KEY=your-secret-key-here
TELEGRAM_BOT_TOKEN=your-bot-token-here
DATABASE_URL=sqlite:///tattoo_gallery.db
```

## 📁 Struttura del Progetto

```
tattoo/
├── bot.py                          # Bot Telegram principale
├── tattoo_gallery/                 # Backend Django
│   ├── manage.py
│   ├── tattoo_gallery/            # Settings Django
│   └── gallery/                   # App principale
│       ├── models.py             # Modelli database
│       ├── views.py              # API endpoints
│       ├── templates/            # Template Django
│       └── migrations/           # Migrazioni DB
├── test_romastudiotattoo/         # File statici pubblici
│   ├── index.html                # Homepage
│   ├── gallery.html              # Galleria principale
│   ├── upload-guide.html         # Guida per tatuatori
│   ├── style.css                 # Stili CSS
│   └── images/                   # Immagini caricati
├── apache_proxy_config.txt        # Configurazione Apache
├── django-gallery.service         # Servizio systemd Django
├── tattoo-bot.service            # Servizio systemd Bot
└── README.md                     # Questa documentazione
```

## 🔐 Sicurezza

- **Isolamento Backend**: Django eseguito solo su localhost
- **Proxy Sicuro**: Apache gestisce tutte le richieste esterne
- **Validazione Input**: Sanitizzazione completa dei dati
- **Backup Automatici**: Sistema di recovery integrato
- **Monitoraggio**: Logs dettagliati per auditing

## 📈 Monitoraggio e Manutenzione

### Comandi Utili
```bash
# Verifica stato servizi
sudo systemctl status django-gallery
sudo systemctl status tattoo-bot

# Visualizza logs
sudo journalctl -u django-gallery -f
sudo journalctl -u tattoo-bot -f

# Backup database
python manage.py dumpdata > backup.json

# Aggiorna galleria
python update_gallery.py
```

### Metriche Disponibili
- Numero totale tatuaggi caricati
- Visualizzazioni per artista
- Tasso di conversione contatti
- Performance sistema

## 🤝 Contributi

Contributi benvenuti! Per modifiche significative:

1. Fork il progetto
2. Crea un branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit le modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📝 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi il file `LICENSE` per maggiori dettagli.

## 📞 Supporto

- **📧 Email**: info@romastudiotattoo.com
- **💬 Telegram**: @roma_studio_support
- **📱 WhatsApp**: +39 3510120753
- **🌐 Sito Web**: [servicess.net](https://servicess.net/articoli/ricontatti.html)

## 🙏 Riconoscimenti

- **Django Framework**: Per il robusto backend web
- **Telegram Bot API**: Per l'integrazione seamless
- **Apache HTTP Server**: Per il proxy sicuro e performante
- **Community Open Source**: Per gli strumenti che rendono possibile questo progetto

---

**Creato con ❤️ per la community dei tatuatori italiani**

⭐ Se questo progetto ti è utile, considera di mettere una stella su GitHub!
