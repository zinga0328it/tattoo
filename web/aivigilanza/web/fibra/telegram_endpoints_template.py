# Template per implementazione endpoint Telegram nel backend FTTH
# Questo file va aggiunto al backend FastAPI sul PC aaa@aaa-aaa

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import os
from typing import Optional

router = APIRouter()

# Configurazione Telegram (da aggiungere alle variabili d'ambiente)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8296100727:AAHVXF0PT9BKown81BuV-jMcYTS7hstTnL8')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '7586394272')

# Stato autorizzazione GPT (in produzione usare database)
gpt_authorized = False

class TelegramStatusResponse(BaseModel):
    bot_active: bool
    bot_username: Optional[str] = None
    webhook_configured: bool = False
    gpt_authorized: bool
    enable_gpt_button: bool
    chat_id: str

class SendTelegramRequest(BaseModel):
    action: str
    chat_id: str
    text: str

def send_telegram_message(text: str, chat_id: str) -> dict:
    """Invia messaggio Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }

        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()

        result = response.json()
        if result.get("ok"):
            return {
                "success": True,
                "message_id": result["result"]["message_id"]
            }
        else:
            raise HTTPException(status_code=500, detail="Errore invio Telegram")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Errore connessione Telegram: {str(e)}")

def get_bot_info() -> dict:
    """Ottieni informazioni del bot"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except:
        return {"ok": False}

@router.get("/telegram/status")
async def get_telegram_status():
    """Restituisce lo stato del bot Telegram e autorizzazioni GPT"""
    global gpt_authorized

    bot_info = get_bot_info()

    return TelegramStatusResponse(
        bot_active=bot_info.get("ok", False),
        bot_username=bot_info.get("result", {}).get("username") if bot_info.get("ok") else None,
        webhook_configured=False,  # Implementare se necessario
        gpt_authorized=gpt_authorized,
        enable_gpt_button=not gpt_authorized,
        chat_id=TELEGRAM_CHAT_ID
    )

@router.post("/telegram/status")
async def enable_gpt_sending():
    """Abilita l'invio di messaggi da parte del GPT"""
    global gpt_authorized

    if gpt_authorized:
        return {"success": True, "message": "GPT già autorizzato"}

    gpt_authorized = True

    return {
        "success": True,
        "message": "GPT autorizzato a inviare messaggi Telegram"
    }

@router.post("/telegram/send")
async def send_telegram_message_endpoint(request: SendTelegramRequest):
    """Endpoint per inviare messaggi Telegram via GPT Actions"""
    global gpt_authorized

    # Verifica autorizzazione GPT
    if not gpt_authorized:
        raise HTTPException(status_code=403, detail="GPT non autorizzato a inviare messaggi")

    # Verifica action
    if request.action != "sendTelegramMessage":
        raise HTTPException(status_code=400, detail="Action non supportata")

    # Verifica chat_id (per sicurezza, permettere solo chat configurate)
    if request.chat_id != TELEGRAM_CHAT_ID:
        raise HTTPException(status_code=403, detail="Chat ID non autorizzato")

    # Invia messaggio
    result = send_telegram_message(request.text, request.chat_id)

    return result

# Esempio di utilizzo negli altri endpoint
def notify_work_assigned(work_data: dict, technician_chat_id: str = None):
    """Notifica assegnazione lavoro via Telegram"""
    if not technician_chat_id:
        technician_chat_id = TELEGRAM_CHAT_ID

    message = f"""📋 NUOVO LAVORO ASSEGNATO

🔢 WR: {work_data.get('numero_wr', 'N/A')}
👤 Cliente: {work_data.get('nome_cliente', 'N/A')}
📍 Indirizzo: {work_data.get('indirizzo', 'N/A')}
🔧 Tipo: {work_data.get('tipo_lavoro', 'N/A')}
📡 Operatore: {work_data.get('operatore', 'N/A')}

[✅ Accetta] [❌ Rifiuta]
[📍 Navigazione]"""

    try:
        send_telegram_message(message, technician_chat_id)
    except Exception as e:
        print(f"Errore notifica Telegram: {e}")

# Aggiungere questo router al main FastAPI app:
# app.include_router(router, prefix="/api", tags=["telegram"])