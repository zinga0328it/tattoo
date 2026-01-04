# Torciabook - Sistema di Login Ultra-Sicuro

## Contromisure Implementate

### 1. **CAPTCHA**
- Richiede verifica umana per ogni tentativo di login
- Previene attacchi automatizzati

### 2. **Honeypot Fields**
- Campi nascosti che i bot riempiono automaticamente
- Rileva e blocca tentativi di automazione

### 3. **IP Blocking Dinamico**
- Dopo 5 tentativi falliti in 5 minuti → IP bloccato per 5 minuti
- Previene brute force da singoli IP

### 4. **Rate Limiting**
- Massimo 5 tentativi al minuto per IP
- Usa Flask-Limiter per controllo granulare

### 5. **Logging Dettagliato**
- Ogni richiesta loggata con timestamp, IP, User-Agent
- Eventi specifici: login success/fail, CAPTCHA fail, honeypot trigger
- File: `/home/alex/web/eternaai/security.log`

### 6. **Sicurezza Backend**
- Password hashate con bcrypt
- JWT tokens con scadenza 1 ora
- Session management sicuro

### 7. **Middleware di Sicurezza**
- Controllo IP bloccato su ogni richiesta
- Log di ogni accesso non autorizzato

## Come Testare

### 1. Avvia l'applicazione
```bash
cd /home/alex/web/eternaai
python3 app.py
```

### 2. Monitora i log in tempo reale
```bash
python3 monitor_logs.py
```

### 3. Testa il brute force
```bash
python3 brute_force_tester.py http://localhost:5000/login admin
```

### 4. Credenziali di test
- Username: `admin`
- Password: `password123`

## Log Files
- `security.log`: Eventi sicurezza dettagliati
- `brute_force_log.txt`: Log del tester
- `login_attempts.log`: Tentativi login (se abilitato)

## Contromisure Attive
- ✅ CAPTCHA obbligatorio
- ✅ Honeypot detection
- ✅ IP blocking automatico
- ✅ Rate limiting
- ✅ Logging completo
- ✅ Sanitizzazione input
- ✅ Protezione CSRF (timestamp)
- ✅ Lockout client-side

## Monitoraggio
Usa `monitor_logs.py` per vedere in tempo reale tutti i tentativi di attacco e le contromisure attivate.
