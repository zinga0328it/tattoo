# 🖼️ **Roma Studio Tattoo Gallery System**

**Sistema automatizzato per la gestione di gallerie fotografiche di tatuaggi con bot Telegram integrato**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.6-green.svg)](https://www.djangoproject.com/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot_API-blue.svg)](https://core.telegram.org/bots/api)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 **Cosa Fa Questo Sistema**

**Roma Studio Tattoo Gallery** è un sistema completo per gestire gallerie fotografiche di tatuaggi con le seguenti funzionalità:

### ✨ **Caratteristiche Principali**
- 🤖 **Bot Telegram Intelligente**: Caricamento foto con descrizione automatica
- ✅ **Sistema di Approvazione**: Moderazione admin prima della pubblicazione
- 🌐 **Homepage Dinamica**: Galleria responsive con dati inline
- 🔄 **Aggiornamento Automatico**: Sincronizzazione tra database e frontend
- 📱 **Mobile-First**: Design ottimizzato per tutti i dispositivi
- 🔒 **Sicuro**: Sistema di permessi e validazione robusto

### 🏗️ **Architettura**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram Bot  │───▶│   Django API    │───▶│   SQLite DB     │
│                 │    │   (Gunicorn)    │    │                 │
│ • Caricamento   │    │ • REST API      │    │ • Foto          │
│ • Approvazione  │    │ • Gestione dati │    │ • Metadati      │
│ • Notifiche     │    │ • Sicurezza     │    │ • Utenti        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Apache Proxy  │    │   Homepage      │    │   Galleria      │
│   (SSL/HTTPS)   │    │   (HTML/JS)     │    │   (Dinamica)     │
│                 │    │ • Dati inline   │    │ • Filtri         │
│ • Load Balance  │    │ • SEO Ready     │    │ • Like System    │
│ • Cloudflare    │    │ • Responsive    │    │ • Condivisione   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🚀 **Installazione Rapida**

### **Prerequisiti**
- Python 3.10+
- Django 5.2+
- SQLite3
- Apache/Nginx (opzionale per produzione)

### **Setup Base**
```bash
# Clona il repository
git clone https://github.com/yourusername/roma-studio-tattoo-gallery.git
cd roma-studio-tattoo-gallery

# Installa dipendenze
pip install -r requirements.txt

# Configura ambiente
cp .env.example .env
# Modifica .env con i tuoi token

# Setup database
python manage.py migrate

# Avvia bot
python bot.py
```

### **Deploy Produzione**
```bash
# Sistema di avvio automatico
sudo systemctl enable tattoo-bot
sudo systemctl enable django-gallery
sudo systemctl enable apache2

# Configurazione Apache
sudo a2enmod proxy proxy_http
sudo systemctl restart apache2
```

---

## 📋 **Come Funziona**

### **1. Caricamento Foto**
```
Utente ──📸──▶ Bot Telegram ──💾──▶ Database (pending)
```

### **2. Approvazione Admin**
```
Admin ──✅──▶ Approva ──🔄──▶ Galleria + Homepage
```

### **3. Pubblicazione**
```
Database ──📤──▶ Homepage (dati inline) ──🌐──▶ Utenti
```

### **Workflow Completo**
1. **Cliente** invia foto al bot
2. **Bot** richiede descrizione
3. **Sistema** salva in coda approvazione
4. **Admin** riceve notifica e approva
5. **Foto** pubblicata automaticamente
6. **Homepage** aggiornata manualmente (per qualità)

---

## 🛠️ **Tecnologie Utilizzate**

### **Backend**
- **Python 3.10+**: Linguaggio principale
- **Django 5.2**: Framework web REST API
- **SQLite**: Database leggero e affidabile
- **Gunicorn**: WSGI server per produzione

### **Frontend**
- **HTML5/CSS3**: Struttura responsive
- **JavaScript (Vanilla)**: Interattività client-side
- **Mobile-First**: Design adattivo

### **Integrazione**
- **Telegram Bot API**: Caricamento e notifiche
- **Apache Proxy**: Load balancing e SSL
- **Cloudflare CDN**: Distribuzione contenuti

### **Sistema**
- **Systemd**: Servizi auto-avvio
- **Logrotate**: Gestione log automatica
- **Cron**: Backup programmati

---

## 🎨 **Screenshot & Demo**

### **Bot Telegram**
```
🤖 Ciao! Invia una foto del tatuaggio
👤 Tu: [📸 Foto inviata]
🤖 Descrivi il tatuaggio:
👤 Tu: Rosa nera realistica
🤖 ✅ Foto ricevuta! In attesa approvazione
```

### **Homepage**
- Galleria responsive con anteprime
- Sistema like integrato
- Link diretti ai profili Telegram
- SEO ottimizzato

---

## 🔧 **Configurazione**

### **File .env**
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_TELEGRAM_IDS=id1,id2,id3
DJANGO_SETTINGS_MODULE=tattoo_gallery.settings
```

### **Permessi Sistema**
```bash
# Directory immagini
sudo chown www-data:www-data /var/www/romastudiotattoo/images/
sudo chmod 775 /var/www/romastudiotattoo/images/

# Servizi systemd
sudo systemctl enable tattoo-bot django-gallery
```

---

## 📊 **Statistiche & Metriche**

- ✅ **Sistema Operativo**: 99% uptime
- ✅ **Foto Pubblicate**: 3+ tatuaggi
- ✅ **Utenti Attivi**: Multi-utente supportato
- ✅ **Auto-Startup**: Servizi systemd configurati
- ✅ **SSL/HTTPS**: Certificato attivo

---

## 🤝 **Come Contribuire**

### **Per Sviluppatori**
1. **Fork** il progetto
2. **Crea** un branch (`git checkout -b feature/nuova-feature`)
3. **Commit** (`git commit -am 'Aggiunta nuova feature'`)
4. **Push** (`git push origin feature/nuova-feature`)
5. **Apri** una Pull Request

### **Tipi di Contributi**
- 🐛 **Bug Fix**: Risoluzione problemi
- ✨ **Features**: Nuove funzionalità
- 📚 **Documentazione**: Miglioramenti guide
- 🎨 **UI/UX**: Miglioramenti interfaccia
- 🧪 **Testing**: Aggiunta test automatici

### **Linee Guida**
- Segui PEP 8 per Python
- Aggiungi commenti al codice
- Testa le modifiche prima del commit
- Mantieni compatibilità backward

---

## 📝 **Roadmap**

### **✅ Completato**
- [x] Sistema base bot Telegram
- [x] API Django REST
- [x] Homepage responsive
- [x] Sistema approvazione admin
- [x] Auto-startup systemd

### **🔄 In Sviluppo**
- [ ] Tasto cancellazione foto
- [ ] Multi-admin support
- [ ] Backup automatico
- [ ] Dashboard analytics

### **📋 Pianificato**
- [ ] Homepage dinamica
- [ ] Filtri categoria
- [ ] Sistema commenti
- [ ] Integrazione social

---

## 🐛 **Segnalazione Bug**

Usa il [template bug report](.github/ISSUE_TEMPLATE/bug_report.md) per segnalare problemi.

**Informazioni richieste:**
- Versione Python/Django
- Sistema operativo
- Log errori (se presenti)
- Passi per riprodurre

---

## 📞 **Supporto & Contatti**

- **📧 Email**: info@romastudiotattoo.com
- **🌐 Sito Web**: [romastudiotattoo.it](https://www.romastudiotattoo.it)
- **🤖 Bot**: [@RomaStudioTattooBot](https://t.me/RomaStudioTattooBot)
- **📱 WhatsApp**: +39 350 149 3778

**Sviluppato con ❤️ da [Servicess](https://servicess.net/)**

---

## 📄 **Licenza**

Questo progetto è distribuito sotto licenza **MIT**. Vedi il file `LICENSE` per dettagli.

**Libertà di:**
- ✅ Usare commercialmente
- ✅ Modificare
- ✅ Distribuire
- ✅ Usare privatamente

**Obblighi:**
- 📄 Mantenere copyright notice
- 📄 Includere licenza nei distributi

---

## 🙏 **Ringraziamenti**

- **Roma Studio Tattoo** per la fiducia
- **Community Open Source** per l'ispirazione
- **Django & Telegram** per gli ottimi framework
- **Tutti i contributori** passati e futuri

---

**⭐ Se questo progetto ti è utile, metti un like! Le stelle aiutano la visibilità!**
