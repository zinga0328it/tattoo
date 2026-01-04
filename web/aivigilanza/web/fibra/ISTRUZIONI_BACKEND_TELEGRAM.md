# 📱 Istruzioni Backend Telegram - Sistema FTTH

## 🤖 Configurazione Bot Telegram

### 1. Creazione Bot
1. Apri Telegram e cerca `@BotFather`
2. Invia comando `/newbot`
3. Segui le istruzioni per creare il bot
4. Salva il **token** ricevuto (formato: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### 2. Configurazione Sistema
Il bot è già configurato con:
- **Token:** `8122910648:AAFnpoCNExI4Y1J6wRI3BW2Wft8KEcfWKmM`
- **Username:** `@ftth01_bot`
- **Chat ID Default:** `7586394272`

## 📨 Comandi Disponibili

| Comando | Descrizione | Esempio |
|---------|-------------|---------|
| `/start` | Benvenuto e info bot | `/start` |
| `/help` | Mostra comandi disponibili | `/help` |
| `/miei_lavori` | Lista lavori assegnati | `/miei_lavori` |
| `/accetta` | Accetta lavoro assegnato | `/accetta WR-001` |
| `/rifiuta` | Rifiuta lavoro assegnato | `/rifiuta WR-001` |
| `/chiudi` | Chiudi lavoro completato | `/chiudi WR-001` |

## 🔧 API Endpoints Telegram

### Invio Messaggi
```bash
# Invio messaggio diretto
curl -X POST "https://servicess.net/gestionale/telegram/send" \
  -H "X-API-Key: JHzxUzdAK8LJ33Y50MDgLf5E62flYset4MYA6ELpXpU=" \
  -d "chat_id=7586394272&text=Messaggio di test"

# Notifica assegnazione lavoro
curl -X POST "https://servicess.net/gestionale/works/{work_id}/notify" \
  -H "X-API-Key: JHzxUzdAK8LJ33Y50MDgLf5E62flYset4MYA6ELpXpU="
```

### Comandi Bot
```bash
# Lista comandi configurati
curl "https://servicess.net/gestionale/telegram/commands" \
  -H "X-API-Key: JHzxUzdAK8LJ33Y50MDgLf5E62flYset4MYA6ELpXpU="
```

## 👤 Gestione Tecnici Telegram

### Aggiungere Telegram ID a Tecnico
1. Il tecnico deve cercare `@userinfobot` su Telegram
2. Inviare `/start` per ottenere il proprio ID
3. Comunicare l'ID al sistema
4. Aggiornare il tecnico via API:
```bash
curl -X PATCH "https://servicess.net/gestionale/technicians/{id}" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: JHzxUzdAK8LJ33Y50MDgLf5E62flYset4MYA6ELpXpU=" \
  -d '{"telegram_id": "123456789"}'
```

### Creazione Automatica Tecnici
La pagina `manual_entry.html` ora crea automaticamente tecnici quando vengono compilati:
- Campo "Nome Squadra"
- Campo "ID Telegram"
- Campo "Nome Cliente" (diventa nome tecnico)

## 📊 Workflow Completo

### 1. Assegnazione Lavoro
```javascript
// 1. Creare lavoro
POST /manual/works → {id: 123, numero_wr: "WR-001"}

// 2. Assegnare tecnico
PUT /works/123/assign/1

// 3. Inviare notifica
POST /works/123/notify
```

### 2. Interazione Tecnico
- Riceve messaggio Telegram con lavoro assegnato
- Può rispondere con comandi `/accetta`, `/rifiuta`, `/chiudi`
- Sistema aggiorna automaticamente lo stato del lavoro

## ⚠️ Troubleshooting

### Messaggi non arrivano
1. Verificare che il tecnico abbia avviato il bot (`/start`)
2. Controllare che il `telegram_id` sia corretto
3. Verificare connessione internet del backend

### Comandi non funzionano
1. Assicurarsi che il lavoro sia assegnato al tecnico
2. Verificare che il bot sia online
3. Controllare i log del backend

### Errore API
```json
{"error": "Invalid chat_id"}
```
- Verificare che il `telegram_id` sia numerico e valido

## 🔄 Test del Sistema

```bash
# Test completo workflow
1. Creare lavoro in manual_entry.html
2. Assegnare tecnico con telegram_id 7586394272
3. Verificare ricezione messaggio Telegram
4. Testare comandi bot
```

---
*Documentazione aggiornata: 29 Dicembre 2025*
