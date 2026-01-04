# 🔧 Configurazione Interna Sistema FTTH
# File di configurazione per il sistema di gestione lavori fibra ottica
# Generato automaticamente - NON MODIFICARE MANUALMENTE

# 📅 Data generazione: 29 Dicembre 2025
# 📍 Percorso file: /home/alex/web/aivigilanza/web/fibra/configurazione_interna.yaml

---

# 🌐 Configurazione Rete e Architettura
network:
  # Yggdrasil IPv6 Mesh Network
  yggdrasil:
    enabled: true
    backend_address: "200:421e:6385:4a8b:dca7:cfb:197f:e9c3"
    backend_port: 6030
    frontend_address: "200:421e:6385:4a8b:dca7:cfb:197f:e9c3"  # stesso PC per ora

  # Apache Proxy Pubblico
  apache:
    enabled: true
    public_domain: "servicess.net"
    public_port: 443
    ssl_enabled: true
    proxy_pass: "/gestionale/"
    auto_inject_api_key: true

# 📁 Struttura Directory
paths:
  # Directory di sviluppo (PC locale)
  development:
    root: "/home/alex/web/aivigilanza"
    web: "/home/alex/web/aivigilanza/web"
    fibra: "/home/alex/web/aivigilanza/web/fibra"
    static: "/home/alex/web/aivigilanza/static"
    templates: "/home/alex/web/aivigilanza/templates"

  # Directory di produzione (Apache)
  production:
    apache_root: "/var/www"
    aivigilanza: "/var/www/aivigilanza"
    fibra: "/var/www/aivigilanza/fibra"
    ssl_certs: "/etc/letsencrypt/live/servicess.net"
    apache_sites: "/etc/apache2/sites-available"
    apache_config: "/etc/apache2/sites-available/servicess.net-ssl.conf"

  # Directory backend (PC remoto)
  backend:
    root: "/home/aaa"
    fibra: "/home/aaa/fibra"
    database: "/home/aaa/fibra/ftth.db"
    logs: "/home/aaa/fibra/logs"
    venv: "/home/aaa/fibra/venv"

# 🔑 Configurazione Sicurezza
security:
  # API Key per autenticazione backend
  api_key: "JHzxUzdAK8LJ33Y50MDgLf5E62flYset4MYA6ELpXpU="

  # JWT per autenticazione admin
  jwt:
    enabled: true
    secret_key: "your-jwt-secret-key-here"
    algorithm: "HS256"
    expiration_hours: 24

  # Telegram Bot
  telegram:
    enabled: true
    bot_token: "8122910648:AAFnpoCNExI4Y1J6wRI3BW2Wft8KEcfWKmM"
    bot_username: "@ftth01_bot"
    default_chat_id: "7586394272"
    gpt_enabled: true

# 🗄️ Configurazione Database
database:
  type: "sqlite"
  path: "/home/aaa/fibra/ftth.db"
  backup_enabled: true
  backup_interval_hours: 24
  max_backups: 7

# 📊 Configurazione API
api:
  # Backend FastAPI
  backend:
    base_url: "http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:6030"
    timeout_seconds: 30
    retry_attempts: 3

  # Frontend pubblico (Apache proxy)
  frontend:
    base_url: "https://servicess.net/gestionale"
    cors_origins:
      - "https://servicess.net"
      - "https://chat.openai.com"

# 📱 Configurazione Frontend
frontend:
  theme: "bootstrap5"
  language: "it"
  timezone: "Europe/Rome"

  # File principali
  files:
    index: "index.html"
    gestionale: "gestionale-ftth.html"
    dashboard: "dashboard.html"
    manual_entry: "manual_entry.html"
    db_viewer: "db_viewer.html"

  # Configurazione JavaScript
  js_config:
    api_base: "http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:6030"
    api_key: "JHzxUzdAK8LJ33Y50MDgLf5E62flYset4MYA6ELpXpU="
    debug_mode: false

# 🔄 Configurazione Servizi
services:
  # Apache Web Server
  apache:
    enabled: true
    service_name: "apache2"
    config_file: "/etc/apache2/sites-available/servicess.net-ssl.conf"
    document_root: "/var/www/aivigilanza"
    server_name: "servicess.net"
    ssl_certificate: "/etc/letsencrypt/live/servicess.net/fullchain.pem"
    ssl_key: "/etc/letsencrypt/live/servicess.net/privkey.pem"

  # Backend FastAPI
  backend_api:
    enabled: true
    service_name: "ftth-backend"
    command: "uvicorn app.main:app --host :: --port 6030 --workers 4"
    working_directory: "/home/aaa/fibra"
    virtual_env: "/home/aaa/fibra/venv"
    auto_restart: true

  # Yggdrasil Network
  yggdrasil:
    enabled: true
    service_name: "yggdrasil"
    config_file: "/etc/yggdrasil.conf"
    peers:
      - "tcp://yggdrasil.example.com:12345"

# 📊 Configurazione Monitoraggio
monitoring:
  enabled: true
  health_check_endpoint: "/health/"
  metrics_endpoint: "/metrics/"
  log_level: "INFO"
  log_file: "/var/log/aivigilanza/ftth.log"

# 🚀 Configurazione Deploy
deploy:
  method: "rsync"
  source: "/home/alex/web/aivigilanza/web/fibra/"
  destination: "/var/www/aivigilanza/fibra/"
  exclude:
    - "*.log"
    - "*.tmp"
    - ".git*"
    - "node_modules/"

# 🏷️ Metadati Sistema
metadata:
  version: "1.2"
  last_updated: "2025-12-29"
  maintainer: "Servicess.net"
  description: "Sistema di gestione lavori FTTH con Yggdrasil e Telegram - Aggiornato con creazione automatica squadre/tecnici"
  license: "Proprietary"

# ⚙️ Configurazioni Speciali
special:
  # Modalità debug
  debug_mode: false

  # Abilita funzioni beta
  beta_features: true

  # Timeout globale
  global_timeout: 30

  # Cache settings
  cache:
    enabled: true
    ttl_seconds: 3600
    max_size_mb: 100

# 🚀 Nuove Funzionalità Implementate (v1.2)
features:
  # Creazione automatica squadre e tecnici
  auto_team_creation:
    enabled: true
    description: "La pagina manual_entry.html crea automaticamente squadre e tecnici quando vengono compilati i campi corrispondenti"
    implemented_date: "2025-12-29"
    files_modified:
      - "manual_entry.html"
    api_endpoints_used:
      - "POST /teams/"
      - "POST /technicians/"

  # Sistema di cancellazione lavori
  work_cancellation:
    enabled: true
    description: "Sistema completo per cancellazione lavori con nota obbligatoria e notifiche"
    implemented_date: "2025-12-26"
    files_modified:
      - "gestionale-ftth.html"
    features:
      - "Dialog di conferma con nota"
      - "Aggiornamento database"
      - "Notifiche errore/successo"

  # Aggiornamenti UI/UX
  ui_updates:
    implemented_date: "2025-12-26"
    changes:
      - "Titolo cambiato: 'Consegne' → 'Lavori FTTH'"
      - "Link corretti: /static/ → /fibra/"
      - "Captcha aggiunto per sicurezza"
      - "Tecnico rinominato: 'Tecnico Test' → 'Alessandro Pepe'"

  # Workflow completo testato
  tested_workflows:
    - "Creazione lavoro manuale"
    - "Assegnazione tecnico con notifica Telegram"
    - "Cancellazione lavoro con nota"
    - "Creazione automatica squadre/tecnici"
    - "Aggiornamento dashboard in tempo reale"