# Tic-Tac-Toe con AI - Manuale di Installazione e Configurazione

## Panoramica del Progetto

Questo progetto implementa un gioco Tic-Tac-Toe online con intelligenza artificiale, composto da:
- **Frontend**: HTML, CSS, JavaScript per l'interfaccia utente
- **Backend**: Server Flask Python con algoritmo AI per le mosse del computer
- **Deployment**: Apache con proxy per sicurezza e routing

## Struttura dei File

```
gioco/
├── index.html          # Pagina web principale del gioco
├── style.css           # Stili CSS per l'interfaccia
├── script.js           # Logica JavaScript del frontend
├── server.py           # Server Flask per il backend
├── main.py             # Algoritmo AI per le mosse del computer
├── requirements.txt    # Dipendenze Python
└── README.md          # Questo manuale
```

## Componenti del Sistema

### 1. Frontend (index.html, style.css, script.js)

**Caratteristiche:**
- Griglia 3x3 interattiva con design scuro
- Il giocatore usa "X", il computer usa "O"
- Animazioni e feedback visivo
- Gestione vittorie, pareggi ed errori
- Pulsante restart per nuove partite

**Tecnologie:**
- HTML5 per la struttura
- CSS3 con flexbox e grid layout
- JavaScript ES6+ con fetch API per chiamate backend

### 2. Backend (server.py, main.py)

**Server Flask (server.py):**
```python
# Endpoint principale: POST /move
# Riceve: {"board": ["", "", "", "", "", "", "", "", ""]}
# Restituisce: {"row": 1, "col": 2}
```

**Algoritmo AI (main.py):**
- Strategia difensiva: blocca le vittorie dell'avversario
- Strategia offensiva: cerca di vincere quando possibile
- Fallback intelligente: centro > angoli > lati
- Gestisce formati di griglia 3x3 e array lineare

### 3. Configurazione Apache

**Proxy Setup:**
```apache
ProxyPass /gioco/move http://127.0.0.1:5001/move
ProxyPassReverse /gioco/move http://127.0.0.1:5001/move
ProxyPass /gioco !
```

**Sicurezza:**
- Backend Flask non esposto pubblicamente (porta 5001 locale)
- Solo endpoint `/gioco/move` inoltrato al backend
- File statici serviti direttamente da Apache

## Installazione Step-by-Step

### 1. Preparazione Ambiente

```bash
# Creare directory di sviluppo
mkdir -p /home/alex/web/servicess/gioco
cd /home/alex/web/servicess/gioco

# Verificare Python e dipendenze
python3 --version
pip3 install Flask Flask-Cors
```

### 2. Deployment File

```bash
# Copiare file in produzione
cp /home/alex/web/servicess/gioco/* /var/www/eternia/gioco/

# Verificare permessi
ls -la /var/www/eternia/gioco/
```

### 3. Configurazione Apache

```bash
# Editare configurazione SSL
sudo nano /etc/apache2/sites-enabled/eternaai_cloud-le-ssl.conf

# Aggiungere righe proxy prima di "ProxyPass /"
ProxyPass /gioco/move http://127.0.0.1:5001/move
ProxyPassReverse /gioco/move http://127.0.0.1:5001/move
ProxyPass /gioco !

# Ricaricare Apache
sudo systemctl reload apache2
```

### 4. Avvio Backend

```bash
# Avviare server Flask
cd /home/alex/web/servicess/gioco
nohup python3 server.py > server.log 2>&1 &

# Verificare processo attivo
ps aux | grep "python3 server.py"
```

## Testing e Verifica

### 1. Test Backend Locale

```bash
# Test diretto server Flask
curl -X POST http://127.0.0.1:5001/move \
  -H "Content-Type: application/json" \
  -d '{"board": [" ", " ", " ", " ", " ", " ", " ", " ", " "]}'

# Risposta attesa: {"col":1,"row":1}
```

### 2. Test Proxy Pubblico

```bash
# Test tramite Apache proxy
curl -X POST https://eternaai.cloud/gioco/move \
  -H "Content-Type: application/json" \
  -d '{"board": [" ", " ", " ", " ", " ", " ", " ", " ", " "]}' \
  --insecure

# Risposta attesa: {"col":1,"row":1}
```

### 3. Test Frontend

1. Aprire browser su `https://eternaai.cloud/gioco/`
2. Cliccare su una cella della griglia
3. Verificare che il computer risponda con una mossa
4. Testare vittorie, pareggi e restart

## Troubleshooting

### Errori Comuni

**1. "Errore del server" nel gioco:**
```bash
# Verificare che il server Flask sia attivo
ps aux | grep "python3 server.py"

# Riavviare se necessario
cd /home/alex/web/servicess/gioco
python3 server.py &
```

**2. 503 Service Unavailable:**
```bash
# Controllare configurazione Apache
grep -A 5 "ProxyPass /gioco" /etc/apache2/sites-enabled/eternaai_cloud-le-ssl.conf

# Ricaricare configurazione
sudo systemctl reload apache2
```

**3. Cache del browser:**
```bash
# Forzare ricaricamento
Ctrl + Shift + R (Linux/Windows)
Cmd + Shift + R (Mac)
```

### Log e Debug

**Log Apache:**
```bash
sudo tail -f /var/log/apache2/eternaai_error.log
```

**Log Flask:**
```bash
tail -f /home/alex/web/servicess/gioco/server.log
```

**Console Browser:**
- F12 > Console tab
- Cercare errori JavaScript o fetch()

## Sicurezza e Best Practices

### Sicurezza Implementata

1. **Backend Isolato**: Flask su 127.0.0.1:5001 (non pubblico)
2. **Proxy Selettivo**: Solo `/gioco/move` inoltrato al backend
3. **File Protetti**: Codice Python non accessibile via web
4. **CORS Configurato**: Headers appropriati per sicurezza

### Monitoring

```bash
# Verificare processi attivi
ps aux | grep python3 | grep server

# Controllare porte in ascolto
sudo ss -tlnp | grep 5001

# Monitorare connessioni
sudo netstat -tulpn | grep :5001
```

## Manutenzione

### Aggiornamenti Codice

```bash
# Aggiornare frontend
cp /home/alex/web/servicess/gioco/*.{html,css,js} /var/www/eternia/gioco/

# Riavviare backend
pkill -f "python3 server.py"
cd /home/alex/web/servicess/gioco
nohup python3 server.py > server.log 2>&1 &
```

### Backup

```bash
# Backup completo
tar -czf gioco_backup_$(date +%Y%m%d).tar.gz /home/alex/web/servicess/gioco/
```

## Architettura Tecnica

### Flusso delle Richieste

1. **Utente** clicca cella → JavaScript `handleClick()`
2. **Frontend** invia board state → `fetch('/gioco/move')`
3. **Apache** proxy → `http://127.0.0.1:5001/move`
4. **Flask** elabora → `mossa_macchina()` da main.py
5. **AI** calcola mossa → risposta JSON `{"row": x, "col": y}`
6. **Frontend** aggiorna interfaccia → piazza "O" del computer

### Performance

- **Latenza**: ~100-200ms per mossa AI
- **Throughput**: Supporta richieste concorrenti
- **Memory**: ~10MB per processo Flask
- **CPU**: Algoritmo AI O(1) - molto efficiente

## Sviluppi Futuri

### Possibili Miglioramenti

1. **Database**: Salvare statistiche partite
2. **Multiplayer**: Sfide tra giocatori umani  
3. **AI Avanzata**: Algoritmi più sofisticati (minimax)
4. **Mobile**: Responsive design per dispositivi mobili
5. **Animazioni**: Transizioni più fluide per le mosse

### Scaling

Per carichi maggiori:
```bash
# Usare Gunicorn invece di Flask dev server
pip3 install gunicorn
gunicorn -w 4 -b 127.0.0.1:5001 server:app
```

---

**Autore**: Sistema AI Assistant  
**Data**: 26 Settembre 2025  
**Versione**: 1.0  
**URL Produzione**: https://eternaai.cloud/gioco/
