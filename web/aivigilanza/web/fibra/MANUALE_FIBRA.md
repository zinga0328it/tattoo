# 📁 Manuale Cartella FTTH (fibra/)

> **Documentazione completa del sistema di gestione lavori FTTH**  
> Versione: 1.2 | Data: 29 Dicembre 2025

---

## 📋 Indice

1. [Panoramica](#panoramica)
2. [Architettura Sistema](#architettura-sistema)
3. [File della Cartella](#file-della-cartella)
4. [Configurazione Apache](#configurazione-apache)
5. [API Backend](#api-backend)
6. [Bot Telegram](#bot-telegram)
7. [GPT Integration](#gpt-integration)
8. [Autenticazione](#autenticazione)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Panoramica

Questa cartella contiene l'interfaccia web per il **Sistema di Gestione Lavori FTTH** (Fiber To The Home). Il sistema permette di:

- ✅ Gestire lavori di installazione/manutenzione fibra ottica
- ✅ Assegnare lavori ai tecnici sul campo
- ✅ Inviare notifiche Telegram ai tecnici
- ✅ Monitorare statistiche in tempo reale
- ✅ Visualizzare dashboard mobile per tecnici

### Tecnologie Utilizzate

| Componente | Tecnologia |
|------------|------------|
| Frontend | HTML5, CSS3, JavaScript (Vanilla), Bootstrap 5.3 |
| Backend | FastAPI (Python) su PC remoto |
| Database | SQLite (ftth.db) |
| Rete Privata | Yggdrasil IPv6 Mesh Network |
| Proxy Pubblico | Apache 2.4 con SSL (Let's Encrypt) |
| Notifiche | Telegram Bot API |

---

## 🆕 Novità Versione 1.2 (29 Dicembre 2025)

### ✨ Nuove Funzionalità Implementate

#### 🤖 Creazione Automatica Squadre e Tecnici
La pagina `manual_entry.html` ora supporta la **creazione automatica** di squadre e tecnici:

- **Campo "Nome Squadra"**: Crea automaticamente una nuova squadra (o usa esistente)
- **Campo "ID Telegram"**: Crea un nuovo tecnico con Telegram ID
- **Workflow automatico**: Squadra → Tecnico → Assegnazione → Notifica Telegram

**Esempio d'uso:**
1. Compila "Nome Squadra: Squadra Sud"
2. Inserisci "ID Telegram: 7586394272"  
3. Il sistema crea automaticamente la squadra e il tecnico
4. Assegna il lavoro e invia notifica Telegram

#### 🗑️ Sistema di Cancellazione Lavori
Implementato sistema completo per cancellazione lavori:

- **Nota obbligatoria**: Dialog con richiesta motivazione
- **Aggiornamento database**: Rimozione permanente dal DB
- **Feedback visivo**: Notifiche di successo/errore
- **Fix applicato**: Risolto blocco "Funzionalità in sviluppo"

#### 🔒 Miglioramenti Sicurezza
- **Captcha aggiunto**: Verifica "8 + 5 = 13" in `manual_entry.html`
- **Validazione input**: Controlli più rigorosi sui form

#### 🎨 Aggiornamenti UI/UX
- **Titoli corretti**: "Consegne" → "Lavori FTTH" in tutto il sistema
- **Link sistemati**: Corretti percorsi da `/static/` → `/fibra/`
- **Tecnico rinominato**: "Tecnico Test" → "Alessandro Pepe"

### 📊 Squadre Disponibili
| Squadra | Tecnici | Status |
|---------|---------|--------|
| Squadra Principale | 4 tecnici | ✅ Attiva |
| Squadra Test | 1 tecnico | ✅ Attiva |

### 🔄 Workflow Completo Testato
1. ✅ **Creazione lavoro manuale** (`manual_entry.html`)
2. ✅ **Creazione automatica squadra/tecnico**
3. ✅ **Assegnazione lavoro** (`PUT /works/{id}/assign/{tech_id}`)
4. ✅ **Notifica Telegram** (`POST /works/{id}/notify`)
5. ✅ **Cancellazione lavoro** con nota obbligatoria
6. ✅ **Aggiornamento dashboard** in tempo reale

---

## 🏗️ Architettura Sistema

```
┌──────────────────────────────────────────────────────────────┐
│                    INTERNET PUBBLICO                         │
│                         ↓                                    │
│              https://servicess.net/gestionale/               │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│  PC FRONTEND (alex@alex) - servicess.net                     │
│  ─────────────────────────────────────────────────────────   │
│  Apache 2.4 SSL                                              │
│  ├─ Let's Encrypt certificates                               │
│  ├─ ProxyPass /gestionale/ → Backend Yggdrasil               │
│  └─ Auto-inject X-API-Key header                             │
│                                                              │
│  Yggdrasil Address: 200:421e:6385:4a8b:dca7:cfb:197f:e9c3    │
└──────────────────────────────────────────────────────────────┘
                          ↓ Yggdrasil IPv6 Mesh
┌──────────────────────────────────────────────────────────────┐
│  PC BACKEND (aaa@aaa-aaa) - Server FTTH                      │
│  ─────────────────────────────────────────────────────────   │
│  FastAPI + Uvicorn (porta 6030)                              │
│  ├─ SQLite Database (ftth.db)                                │
│  ├─ API REST per works, technicians, teams                   │
│  ├─ Telegram Bot integration                                 │
│  └─ JWT + X-API-Key authentication                           │
│                                                              │
│  Yggdrasil Address: 200:421e:6385:4a8b:dca7:cfb:197f:e9c3    │
│  Porta API: 6030                                             │
└──────────────────────────────────────────────────────────────┘
```

### Flusso delle Richieste

1. **Browser** → `https://servicess.net/gestionale/works/`
2. **Apache** riceve la richiesta HTTPS
3. **Apache** inietta automaticamente header `X-API-Key`
4. **Apache** inoltra a `http://[IPv6_Yggdrasil]:6030/works/`
5. **Backend** elabora e risponde
6. **Apache** restituisce risposta al browser

---

## 📂 File della Cartella

### File Principali

| File | Descrizione | Uso |
|------|-------------|-----|
| `index.html` | **Pannello Admin Principale** | Dashboard con stats, form rapido creazione lavori, gestione Telegram tecnici |
| `gestionale-ftth.html` | **Gestionale Completo** | Interfaccia full-feature per gestione lavori |
| `dashboard.html` | **Dashboard Tecnici** | Interfaccia mobile-first per tecnici sul campo |
| `manual_entry.html` | **Form Completo** | Inserimento lavori con tutti i campi |
| `db_viewer.html` | **Visualizzatore DB** | Tool debug per ispezionare database (richiede JWT) |

### File Backup (Versioni Precedenti)

| File | Data Backup | Modifiche |
|------|-------------|-----------|
| `gestionale-ftth.html.backup` | 26 Dic 2025 | Fix cancellazione, titolo aggiornato |
| `manual_entry.html.backup` | 21 Dic 2025 | Versione senza creazione automatica squadre |
| `index.html.backup` | 21 Dic 2025 | Versione precedente |
| `telegram_status.html.backup` | 21 Dic 2025 | Versione precedente |

### File Documentazione

| File | Descrizione |
|------|-------------|
| `MANUALE_FIBRA.md` | Questo manuale (v1.2 - 29 Dic 2025) |
| `configurazione_interna.md` | Configurazione dettagliata sistema |
| `configurazione_interna.yaml` | File YAML configurazione |
| `ISTRUZIONI_BACKEND_TELEGRAM.md` | Guida completa bot Telegram |
| `README_YGGDRASIL.md` | Guida setup rete Yggdrasil |
| `.gitignore_info` | Marker per escludere da git principale |

---

## 🔧 Configurazione Apache

### File: `/etc/apache2/sites-enabled/servicess.net-ssl.conf`

```apache
# Proxy verso backend Yggdrasil FTTH
ProxyPass /gestionale/ http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:6030/
ProxyPassReverse /gestionale/ http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:6030/

# Iniezione automatica X-API-Key
<Location /gestionale/>
    RequestHeader set X-API-Key "JHzxUzdAK8LJ33Y50MDgLf5E62flYset4MYA6ELpXpU="
    ProxyPreserveHost On
</Location>
```

### Comandi Utili

```bash
# Verificare configurazione
sudo apachectl configtest

# Ricaricare Apache
sudo systemctl reload apache2

# Testare connettività backend
curl -s "https://servicess.net/gestionale/health/"
```

---

## 🌐 API Backend

### Endpoint Pubblici (GET - senza auth)

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/health/` | GET | Health check |
| `/works/` | GET | Lista tutti i lavori |
| `/technicians/` | GET | Lista tecnici |
| `/teams/` | GET | Lista squadre |
| `/stats/weekly` | GET | Statistiche settimanali |
| `/stats/closed_by_operator` | GET | Chiusure per operatore |
| `/stats/closed_by_technician` | GET | Chiusure per tecnico |
| `/stats/daily_closed` | GET | Chiusure giornaliere |
| `/telegram/commands` | GET | Comandi bot configurati |

### Endpoint Protetti (richiedono JWT)

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/works/` | POST | Crea nuovo lavoro |
| `/works/{id}` | PUT | Aggiorna lavoro |
| `/works/{id}/status` | PUT | Cambia stato lavoro |
| `/works/{id}/assign/{tech_id}` | PUT | Assegna tecnico |
| `/works/{id}/notify` | POST | Invia notifica Telegram |
| `/technicians/{id}` | PATCH | Aggiorna tecnico |
| `/teams/` | POST | Crea nuova squadra |
| `/teams/{id}` | PUT/PATCH | Aggiorna squadra |
| `/manual/works` | POST | Creazione manuale lavoro |

### Autenticazione

```bash
# Registrazione utente
curl -X POST "http://backend:6030/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123","role":"admin"}'

# Login (ottieni JWT)
curl -X POST "http://backend:6030/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}'
# Risposta: {"access_token":"eyJ...", "token_type":"bearer"}

# Usa token nelle richieste
curl -X POST "http://backend:6030/works/" \
  -H "Authorization: Bearer eyJ..."
  -H "Content-Type: application/json" \
  -d '{"numero_wr":"WR-001",...}'
```

---

## 🤖 Bot Telegram

### Informazioni Bot

| Proprietà | Valore |
|-----------|--------|
| Nome | Maiori Deals Bot |
| Username | @MaioriDealsBot |
| Bot ID | 7792799425 |

### Comandi Disponibili

| Comando | Descrizione |
|---------|-------------|
| `/start` | Benvenuto |
| `/help` | Mostra comandi |
| `/miei_lavori` | I tuoi lavori assegnati |
| `/accetta` | Accetta un lavoro |
| `/rifiuta` | Rifiuta un lavoro |
| `/chiudi` | Chiudi un lavoro completato |

### Notifiche Lavori

Quando viene assegnato un lavoro a un tecnico con Telegram configurato, riceve:

```
📋 NUOVO LAVORO ASSEGNATO

🔢 WR: WR-001
👤 Cliente: Mario Rossi
📍 Indirizzo: Via Roma 25, Fiumicino
🔧 Tipo: Installazione
📡 Operatore: Open Fiber

[✅ Accetta] [❌ Rifiuta]
[📍 Navigazione]
```

### Configurare Telegram ID Tecnico

1. Il tecnico cerca `@userinfobot` su Telegram
2. Invia `/start` al bot
3. Riceve il proprio Telegram ID numerico
4. In `index.html`, cliccare "📱 Telegram" accanto al tecnico
5. Inserire l'ID e salvare

---

## 🔮 GPT Integration

### Funzionalità

- **Creazione Automatica Lavori**: GPT può generare lavori basati su input naturali.
- **Aggiornamento Stato Lavori**: Modifica dello stato dei lavori tramite comandi GPT.
- **Estrazione Informazioni**: Ottenere dettagli sui lavori chiedendo a GPT.
- **📱 Invio Messaggi Telegram**: GPT può inviare messaggi ai tecnici e alle squadre.

### Esempi di Comandi

- "Crea un lavoro per installare fibra ottica in Via Roma 25."
- "Mostrami lo stato dell'ultimo lavoro assegnato."
- "Chiudi il lavoro WR-001 e informa il tecnico."
- "Invia un messaggio al tecnico Mario: 'Il lavoro è pronto per domani'."

### Endpoint GPT Telegram

#### Abilitazione GPT
```bash
POST /gestionale/telegram/gpt/status
Content-Type: application/json

{"enabled": true}
```

#### Invio Messaggi
```bash
POST /gestionale/telegram/gpt/send
Content-Type: application/json

{
  "action": "send_message",
  "target_type": "technician|team",
  "target_id": 123,
  "message": "Il tuo messaggio qui",
  "work_id": 456  // opzionale
}
```

### Limitazioni

- ✅ Funzionalità completamente operativa
- ✅ Richiede connessione attiva con il backend
- ✅ GPT deve essere abilitato prima dell'uso

---

## 🔐 Autenticazione

### Livelli di Sicurezza

| Livello | Protezione | Uso |
|---------|------------|-----|
| **Rete** | Yggdrasil IPv6 | Backend non esposto su Internet |
| **Proxy** | X-API-Key | Apache inietta automaticamente |
| **API** | JWT Token | Operazioni di scrittura |

### X-API-Key

```
JHzxUzdAK8LJ33Y50MDgLf5E62flYset4MYA6ELpXpU=
```

Generata con: `openssl rand -hex 32`

### Credenziali Admin

| Username | Password | Ruolo |
|----------|----------|-------|
| admin | test123456 | admin |

---

## 🔧 Troubleshooting

### Backend non risponde

```bash
# 1. Verificare Yggdrasil
ping6 200:421e:6385:4a8b:dca7:cfb:197f:e9c3

# 2. Verificare backend attivo
curl -s "http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:6030/health/"

# 3. Sul PC backend, verificare che uvicorn sia attivo con IPv6
uvicorn main:app --host :: --port 6030
```

### Apache 503 Service Unavailable

```bash
# Verificare indirizzo IPv6 in Apache config
grep -A5 "gestionale" /etc/apache2/sites-enabled/servicess.net-ssl.conf

# Ricaricare Apache
sudo systemctl reload apache2
```

### Telegram non invia notifiche

```bash
# Verificare bot attivo
curl -s "https://api.telegram.org/bot7792799425:AAEOVfNjAlxPBXcIcPW7uxRWtRgCKlWloV8/getMe"

# Verificare Telegram ID tecnico
curl -s "https://servicess.net/gestionale/technicians/" | python3 -m json.tool
```

### Errore "Missing credentials"

Gli endpoint di scrittura richiedono JWT. Effettuare login prima:

```bash
# Login
TOKEN=$(curl -s -X POST "http://backend:6030/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"test123456"}' | jq -r '.access_token')

# Usa token
curl -X POST "http://backend:6030/works/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"numero_wr":"WR-NEW",...}'
```

---

## 📊 Statistiche Sistema (20/12/2025)

| Metrica | Valore |
|---------|--------|
| Lavori totali | 25+ |
| Chiusi questa settimana | 4 |
| Tecnici | 1 |
| Squadre | 1 |
| Bot Telegram | ✅ Attivo |
| API Backend | ✅ Operativo |
| GPT Integration | ✅ Operativo (lettura/scrittura + Telegram) |
| Endpoint GPT Telegram | ✅ Implementati e testati |

---

## 📞 Contatti

- **Progetto**: Servicess.net - Sistema FTTH
- **Maintainer**: Team Servicess
- **Ultimo aggiornamento**: 20 Dicembre 2025
