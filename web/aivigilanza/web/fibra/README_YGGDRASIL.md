# 🌐 Gestionale FTTH via Yggdrasil

Sistema di gestione consegne FTTH con architettura client-server tramite rete Yggdrasil.

---

## 📐 Architettura

```
┌─────────────────────────────────────┐
│  PC PRINCIPALE (Backend)            │
│  Indirizzo Yggdrasil: 200:xxxx...   │
│  Porta API: 6030                    │
│  ├─ Python Flask API (works)        │
│  ├─ SQLite Database                 │
│  └─ X-API-Key Protection            │
└─────────────────────────────────────┘
              ↕ Yggdrasil Network
┌─────────────────────────────────────┐
│  PC SECONDARIO (Frontend)           │
│  Indirizzo Yggdrasil: 200:yyyy...   │
│  Porta Web: 80 o 8080               │
│  ├─ gestionale-ftth.html                 │
│  └─ nginx o Python http.server      │
└─────────────────────────────────────┘
```

---

## 🖥️ PC PRINCIPALE - Setup Backend

### 1. Installa Yggdrasil

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install yggdrasil

# Avvia servizio
sudo systemctl enable yggdrasil
sudo systemctl start yggdrasil

# Verifica indirizzo IPv6
sudo yggdrasilctl getSelf
# Output esempio: 200:421e:6385:4a8b:dca7:cfb:197f:e9c3
```

### 2. Backend Python (NON in questo repo)

Il backend Python **non è in questo repository**. È presente su un altro PC e deve:

- Ascoltare su `0.0.0.0:6030` (tutte le interfacce)
- Esporre endpoint `/works/` con metodi GET/PUT/POST/DELETE
- Richiedere header `X-API-Key` per autenticazione

### 3. Configura Firewall

```bash
# Permetti traffico sulla porta 6030 da Yggdrasil
sudo ufw allow 6030/tcp comment "API FTTH Gestionale"
sudo ufw reload
```

### 4. Test API Locale

```bash
# Verifica che l'API risponda
curl http://localhost:6030/health

# Test con X-API-Key (se richiesta)
curl -H "X-API-Key: TUA_CHIAVE" http://localhost:6030/works/
```

---

## 🖥️ PC SECONDARIO - Setup Frontend

### 1. Installa Yggdrasil

```bash
sudo apt update
sudo apt install yggdrasil
sudo systemctl enable yggdrasil
sudo systemctl start yggdrasil

# Verifica indirizzo
sudo yggdrasilctl getSelf
```

### 2. Scarica il Frontend

```bash
# Copia gestionale-ftth.html dal PC principale o da questo repo
cd /tmp
scp user@server:/home/alex/web/aivigilanza/web/fibra/gestionale-ftth.html .

# Oppure scarica direttamente se disponibile via web
```

### 3. Modifica Configurazione API

Apri `gestionale-ftth.html` e modifica la riga con `API_BASE`:

```javascript
// PRIMA (default localhost):
const API_BASE = `${_loc.protocol}//${_loc.hostname}:6030`;

// DOPO (Yggdrasil PC principale):
const API_BASE = 'http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:6030';
```

**Sostituisci** `200:421e:6385:4a8b:dca7:cfb:197f:e9c3` con l'**indirizzo Yggdrasil reale** del PC principale.

### 4. Configura X-API-Key (se necessario)

Se il backend richiede autenticazione, decomment questa riga in `gestionale-ftth.html`:

```javascript
function apiFetch(path, opts = {}) {
    const base = window.__API_BASE__ || API_BASE;
    const url = base ? base + path : path;
    
    if (!opts.headers) opts.headers = {};
    opts.headers['X-API-Key'] = 'TUA_API_KEY_QUI'; // <-- Inserisci la chiave
    
    return fetch(url, opts);
}
```

### 5. Installa Web Server

#### Opzione A: Python (rapido)

```bash
cd /path/to/gestionale/
python3 -m http.server 8080

# Accedi da browser: http://localhost:8080/gestionale-ftth.html
```

#### Opzione B: Nginx (produzione)

```bash
sudo apt install nginx

# Crea directory
sudo mkdir -p /var/www/ftth
sudo cp gestionale-ftth.html /var/www/ftth/

# Configura nginx
sudo tee /etc/nginx/sites-available/ftth << 'EOF'
server {
    listen 80;
    listen [::]:80;
    
    root /var/www/ftth;
    index gestionale-ftth.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
}
EOF

# Abilita sito
sudo ln -s /etc/nginx/sites-available/ftth /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. Apri Firewall (se necessario)

```bash
sudo ufw allow 80/tcp comment "Gestionale FTTH Web"
sudo ufw reload
```

---

## 🧪 Test Connessione

### Da PC Secondario

```bash
# 1. Ping Yggdrasil PC principale
ping6 200:421e:6385:4a8b:dca7:cfb:197f:e9c3

# 2. Test porta API
curl -6 http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:6030/health

# 3. Test con X-API-Key
curl -6 -H "X-API-Key: TUA_KEY" \
  http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:6030/works/
```

### Dal Browser

1. Apri `http://localhost:8080/gestionale-ftth.html` (o IP Yggdrasil del PC secondario)
2. Controlla la console browser (F12) per errori di connessione
3. Dovresti vedere le statistiche e gli ordini caricati

---

## 🔒 Sicurezza X-API-Key

### Generare una API Key Sicura

```bash
# Su Linux/Mac
openssl rand -hex 32

# Oppure Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Configurare sul Backend

Nel file Python del backend:

```python
API_KEY = os.getenv('API_KEY', 'LA_CHIAVE_GENERATA')

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('x-api-key') or request.headers.get('X-API-Key')
        if not api_key or api_key != API_KEY:
            return jsonify({'error': 'API Key non valida'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/works/', methods=['GET'])
@require_api_key
def get_works():
    # ...
```

### Configurare sul Frontend

In `gestionale-ftth.html`, linea ~483:

```javascript
opts.headers['X-API-Key'] = 'STESSA_CHIAVE_DEL_BACKEND';
```

---

## 📦 File Inclusi

```
/home/alex/web/aivigilanza/web/fibra/
├── gestionale-ftth.html       ← Frontend completo con CSS/JS inline
└── README_YGGDRASIL.md   ← Questo file
```

**NOTA:** Il backend Python NON è incluso in questo repo. È su un altro PC.

---

## 🚨 Troubleshooting

### Errore: "Errore caricamento ordini"

```bash
# Verifica connessione Yggdrasil
ping6 [indirizzo-pc-principale]

# Verifica firewall
sudo ufw status
```

### Errore 401 Unauthorized

- Verifica che la `X-API-Key` sia identica su backend e frontend
- Controlla console browser per l'header inviato

### Ordini non si aggiornano

- Controlla che il backend stia ascoltando su `0.0.0.0:6030` e non `127.0.0.1`
- Verifica permessi database SQLite sul backend

### Mappa non funziona

- La geocodifica usa Nominatim (OpenStreetMap), richiede connessione Internet
- Rispetta i limiti di rate (1 req/sec)

---

## 📝 Esempio Completo

### PC Principale (Backend)

```bash
# Indirizzo Yggdrasil
sudo yggdrasilctl getSelf
# → 200:421e:6385:4a8b:dca7:cfb:197f:e9c3

# Backend in ascolto
python3 backend_ftth.py
# → Server running on 0.0.0.0:6030
```

### PC Secondario (Frontend)

```bash
# Modifica gestionale-ftth.html
nano gestionale-ftth.html
# → Cambia API_BASE in http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:6030

# Avvia web server
python3 -m http.server 8080

# Apri browser
firefox http://localhost:8080/gestionale-ftth.html
```

---

**Fine Documentazione Yggdrasil - FTTH Gestionale**
