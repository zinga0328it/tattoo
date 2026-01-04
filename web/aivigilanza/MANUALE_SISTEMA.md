# 📚 Manuale Sistema Servicess.net

**Autore:** Sistema di Documentazione Automatica  
**Data:** 14 Dicembre 2025  
**Versione:** 2.0  

---

## 📁 Struttura del Progetto

```
/home/alex/web/aivigilanza/        ← Sorgenti Python (sviluppo)
├── consenso.py                    ← FastAPI GDPR (porta 8000)
├── python/
│   ├── backend.py                 ← Flask contratti (porta 5501)
│   ├── guardiania.py              ← Generatore PDF guardiania
│   ├── pulizie.py                 ← Generatore PDF pulizie
│   └── ricontatti.py              ← Generatore PDF ricontatti
├── shop/consegne/
│   └── carrello.py                ← Flask carrello HTTPS (porta 5504)
├── dati_privati/                  ← Database SQLite (non pubblico)
└── web/                           ← File HTML di sviluppo

/var/www/aivigilanza/              ← DocumentRoot Apache (PRODUZIONE)
├── *.html                         ← Pagine pubbliche
├── articoli/                      ← Articoli e landing page
├── contratti/                     ← PDF contratti generati
└── traduzione/                    ← File JS traduzioni
```

---

## 🔌 Servizi Backend (Systemd)

| Servizio | Porta | Tipo | Descrizione |
|----------|-------|------|-------------|
| `consenso.service` | 8000 | FastAPI | Gestione consensi GDPR |
| `backend.service` | 5501 | Flask | Generazione contratti PDF |
| `carrello.service` | 5504 | Flask HTTPS | Carrello ordini + Telegram Bot |
| `contatore.service` | 2626 | Python | Contatore visite |

### Comandi Utili

```bash
# Stato servizi
sudo systemctl status consenso backend carrello contatore

# Riavvia un servizio
sudo systemctl restart backend.service

# Vedi log in tempo reale
sudo journalctl -u backend.service -f

# Ricarica dopo modifica
sudo systemctl daemon-reload
sudo systemctl restart backend.service
```

---

## 🔐 Sicurezza API (X-API-Key)

### Sistema di Autenticazione

Il sistema `carrello.py` usa autenticazione tramite header **X-API-Key** per proteggere gli endpoint del gestionale.

```python
# Esempio decorator protezione (carrello.py)
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('x-api-key') or request.headers.get('X-API-Key')
        if not api_key or api_key != API_KEY:
            return jsonify({'error': 'API Key non valida o mancante'}), 401
        return f(*args, **kwargs)
    return decorated
```

### Endpoint Protetti (richiedono X-API-Key)

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/api/gestionale/ordini` | GET | Lista tutti gli ordini |
| `/api/gestionale/ordine/<id>/stato` | PUT | Cambia stato ordine |
| `/api/gestionale/utenti` | GET | Lista utenti |
| `/api/gestionale/utente/<tel>/ban` | POST | Banna/Sbanna utente |

### Endpoint Pubblici (NO API Key)

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/api/prodotti` | GET | Lista prodotti disponibili |
| `/api/ordine` | POST | Crea nuovo ordine |
| `/api/ip` | GET | IP del client (GDPR) |
| `/invia-consenso` | POST | Registra consenso privacy |
| `/genera-contratto` | POST | Genera PDF guardiania |
| `/genera-contratto-pulizie` | POST | Genera PDF pulizie |
| `/genera-contratto-ricontatto` | POST | Genera PDF ricontatto |

### Come Usare l'API Key

```javascript
// JavaScript
fetch('/api/gestionale/ordini', {
    headers: {
        'X-API-Key': 'la-tua-api-key-segreta'
    }
})

// cURL
curl -H "X-API-Key: la-tua-api-key-segreta" \
     https://servicess.net/api/gestionale/ordini
```

### Dove Trovare/Cambiare l'API Key

```bash
# L'API Key è in .env o generata automaticamente
cat /home/alex/web/aivigilanza/shop/consegne/.env

# Variabile d'ambiente
API_KEY=tua_chiave_segreta_qui
```

---

## 🔄 Flusso Dati

```
Client Browser
     │
     ▼
Apache :443 (SSL/HTTPS)
     │
     ├── /api/ip → FastAPI :8000 (consenso.py)
     ├── /invia-consenso → FastAPI :8000
     │
     ├── /genera-contratto → Flask :5501 (backend.py)
     ├── /genera-contratto-pulizie → Flask :5501
     ├── /genera-contratto-ricontatto → Flask :5501
     │
     ├── /api/prodotti → Flask :5504 HTTPS (carrello.py)
     ├── /api/ordine → Flask :5504
     └── /api/gestionale/* → Flask :5504 (X-API-Key required)
```

---

## 📄 Generazione Contratti PDF

### Contratto Guardiania

```javascript
// POST /genera-contratto
{
    "nome_cliente": "Mario Rossi",
    "indirizzo_cliente": "Via Roma 1, 00100 Roma",
    "cf_cliente": "RSSMRA80A01H501Z",
    "numero_operatori": 10,
    "durata_ore": 4,
    "tariffa_oraria": 20.0,
    "data_inizio": "2025-01-15",
    "durata_giorni": 1,
    "luogo": "Roma"
}
```

### Contratto Pulizie

```javascript
// POST /genera-contratto-pulizie
{
    "nome_cliente": "Mario Rossi",
    "tipo_servizio": "straordinarie",  // ordinarie €15, straordinarie/sanificazione €20
    "numero_operatori": 2,
    "ore_totali": 4,
    "luogo": "Roma"
}
```

### Richiesta Ricontatto

```javascript
// POST /genera-contratto-ricontatto
{
    "nome": "Mario",
    "cognome": "Rossi",
    "email": "mario@email.it",
    "telefono": "333 1234567",
    "tipo_servizio": "vigilanza",  // vigilanza, pulizie, sicurezza, web, altro
    "descrizione_richiesta": "Vorrei informazioni...",
    "privacy_accettata": true,
    "contratto_accettato": true
}
```

---

## 🤖 Integrazione Telegram

### Configurazione Bot

```bash
# Variabili ambiente (.env)
TELEGRAM_BOT_TOKEN=8122910648:AAFnpoCNExI4Y1J6wRI3BW2Wft8KEcfWKmM
TELEGRAM_CHAT_ID=7586394272
```

### Notifiche Automatiche

| Evento | Notifica |
|--------|----------|
| Nuovo ordine carrello | ✅ Dettagli ordine + bottoni gestione |
| Nuova richiesta ricontatto | 🔔 Dati cliente + servizio richiesto |
| Cambio stato ordine | 📦 Aggiornamento stato |

### Comandi Bot Telegram

```
/start - Attiva ricezione notifiche
/ordini - Lista ordini in attesa
/completato <codice> - Segna ordine completato
/annullato <codice> - Annulla ordine
```

---

## 🗄️ Database

### Percorsi Database

| Database | Percorso | Contenuto |
|----------|----------|-----------|
| Consensi GDPR | `/home/alex/web/aivigilanza/dati_privati/consensi.db` | Registrazioni privacy |
| Ordini Carrello | `/home/alex/web/aivigilanza/shop/consegne/ordini.db` | Ordini, utenti, prodotti |

### Schema Consensi

```sql
CREATE TABLE consensi (
    id INTEGER PRIMARY KEY,
    nome TEXT,
    cognome TEXT,
    indirizzo TEXT,
    cap TEXT,
    citta TEXT,
    provincia TEXT,
    telefono TEXT,
    consenso_privacy INTEGER,
    consenso_cookie INTEGER,
    ip_address TEXT,
    user_agent TEXT,
    hash_consenso TEXT,
    timestamp TEXT
);
```

### Schema Ordini

```sql
CREATE TABLE ordini (
    id INTEGER PRIMARY KEY,
    codice_conferma TEXT UNIQUE,
    telefono TEXT,
    indirizzo_consegna TEXT,
    prodotti TEXT,
    totale REAL,
    stato TEXT DEFAULT 'in_attesa',
    note TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE utenti (
    telefono TEXT PRIMARY KEY,
    nome TEXT,
    ordini_totali INTEGER,
    ordini_completati INTEGER,
    valutazione REAL DEFAULT 5.0,
    banned INTEGER DEFAULT 0
);
```

---

## 🌐 Configurazione Apache

### Virtual Host SSL

```apache
# /etc/apache2/sites-enabled/servicess.net-ssl.conf

ServerName aivigilanza.it
ServerAlias servicess.net www.servicess.net

# Proxy verso backend Python
ProxyPass /api/ip http://127.0.0.1:8000/api/ip
ProxyPass /invia-consenso http://127.0.0.1:8000/invia-consenso
ProxyPass /genera-contratto http://127.0.0.1:5501/genera-contratto
ProxyPass /api/prodotti https://127.0.0.1:5504/api/prodotti
ProxyPass /api/gestionale/ https://127.0.0.1:5504/api/gestionale/

DocumentRoot /var/www/aivigilanza
```

### Comandi Apache

```bash
# Test configurazione
sudo apache2ctl configtest

# Riavvia Apache
sudo systemctl reload apache2

# Abilita moduli necessari
sudo a2enmod proxy proxy_http ssl headers
```

---

## 📋 Dati Aziendali

```
Ragione Sociale: Servicess.net di Alessandro Pepe
Indirizzo:       Via G. Galopini, 1
CAP/Città:       00133 Roma (RM)
P.IVA:           10807641005
Codice Fiscale:  PPELSN79M18H501R
IBAN:            IT60X0760103200001060193837
Email:           info@servicess.net
Sito:            https://servicess.net
```

---

## 🛠️ Manutenzione

### Backup Database

```bash
# Backup manuale
cp /home/alex/web/aivigilanza/dati_privati/consensi.db \
   /home/alex/web/aivigilanza/dati_privati/backup/consensi_$(date +%Y%m%d).db

cp /home/alex/web/aivigilanza/shop/consegne/ordini.db \
   /home/alex/web/aivigilanza/shop/consegne/backup/ordini_$(date +%Y%m%d).db
```

### Deploy Modifiche HTML

```bash
# Copia da sviluppo a produzione
sudo cp /home/alex/web/aivigilanza/web/*.html /var/www/aivigilanza/
sudo cp /home/alex/web/aivigilanza/web/articoli/*.html /var/www/aivigilanza/articoli/
```

### Aggiornamento Python

```bash
# Dopo modifica a file .py
sudo systemctl restart backend.service
sudo systemctl restart consenso.service
sudo systemctl restart carrello.service
```

### Verifica Porte

```bash
# Controlla porte in ascolto
sudo netstat -tlnp | grep -E '5501|5504|8000|2626'

# Oppure
sudo ss -tlnp | grep -E '5501|5504|8000|2626'
```

---

## 🚨 Troubleshooting

### Errore 503 Service Unavailable
```bash
# Verifica se il servizio è attivo
sudo systemctl status backend.service
sudo systemctl status consenso.service

# Se down, riavvia
sudo systemctl restart backend.service
```

### Errore 401 Unauthorized
```bash
# Manca header X-API-Key
# Verifica di aver incluso l'header correttamente
```

### PDF non generato
```bash
# Controlla permessi cartella contratti
ls -la /var/www/aivigilanza/contratti/
sudo chown -R alex:www-data /var/www/aivigilanza/contratti/
sudo chmod 775 /var/www/aivigilanza/contratti/
```

### Telegram non riceve notifiche
```bash
# Verifica token bot
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe"

# Verifica chat ID
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getUpdates"
```

---

## 📝 Checklist Deploy

- [ ] Tutti i servizi systemd attivi
- [ ] Apache ricaricato dopo modifica conf
- [ ] File HTML copiati in /var/www
- [ ] Database con permessi corretti
- [ ] Certificati SSL validi (Let's Encrypt)
- [ ] Backup database effettuato
- [ ] Test endpoint principali OK

---

---

**Fine Manuale - Servicess.net © 2025**
