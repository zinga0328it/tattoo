#!/usr/bin/env python3
"""
Backend FastAPI per gestione consensi GDPR
Porta: 8000
Endpoints:
  - GET /api/ip → IP del client
  - POST /invia-consenso → Registra consenso
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sqlite3
import hashlib
import os
from datetime import datetime

# === CONFIGURAZIONE ===
DB_PATH = "/home/alex/web/aivigilanza/dati_privati/consensi.db"
PORT = 8000

app = FastAPI(title="Consenso GDPR API", version="1.0")

# CORS - Configurato per GPT/OpenAI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://chat.openai.com",  # GPT Actions
        "https://servicess.net",    # Dominio principale
        "http://localhost:3000",   # Sviluppo locale
        "http://127.0.0.1:3000",   # Sviluppo locale
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# === DATABASE ===
def init_db():
    """Inizializza il database consensi"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS consensi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cognome TEXT NOT NULL,
            indirizzo TEXT NOT NULL,
            cap TEXT NOT NULL,
            citta TEXT NOT NULL,
            provincia TEXT NOT NULL,
            telefono TEXT,
            consenso_privacy INTEGER NOT NULL,
            consenso_cookie INTEGER NOT NULL,
            ip_address TEXT NOT NULL,
            user_agent TEXT,
            hash_consenso TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print(f"✅ Database inizializzato: {DB_PATH}")

def get_client_ip(request: Request) -> str:
    """Estrae l'IP reale del client (considera proxy)"""
    # Header comuni per proxy
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback
    return request.client.host if request.client else "unknown"

def genera_hash_consenso(dati: dict) -> str:
    """Genera hash univoco per il consenso"""
    stringa = f"{dati['nome']}{dati['cognome']}{dati['timestamp']}{dati['ip']}"
    return hashlib.sha256(stringa.encode()).hexdigest()[:32]

# === ENDPOINTS ===

@app.get("/api/ip")
async def get_ip(request: Request):
    """Restituisce l'IP del client"""
    ip = get_client_ip(request)
    return {"ip": ip}

@app.post("/invia-consenso")
async def invia_consenso(
    request: Request,
    nome: str = Form(...),
    cognome: str = Form(...),
    indirizzo: str = Form(...),
    cap: str = Form(...),
    citta: str = Form(...),
    provincia: str = Form(...),
    telefono: str = Form(None),
    consenso_privacy: str = Form(...),
    consenso_cookie: str = Form(...),
    captcha_answer: str = Form(None),
    captcha_expected: str = Form(None),
    captcha_question: str = Form(None)
):
    """Registra un nuovo consenso GDPR"""
    try:
        # Validazione CAPTCHA (opzionale server-side)
        if captcha_answer and captcha_expected:
            try:
                if int(captcha_answer) != int(captcha_expected):
                    return JSONResponse(
                        status_code=400,
                        content={"errore": "CAPTCHA non valido"}
                    )
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"errore": "Risposta CAPTCHA non valida"}
                )
        
        # Dati consenso
        ip = get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        dati = {
            "nome": nome,
            "cognome": cognome,
            "timestamp": timestamp,
            "ip": ip
        }
        hash_consenso = genera_hash_consenso(dati)
        
        # Salva nel database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO consensi 
            (nome, cognome, indirizzo, cap, citta, provincia, telefono, 
             consenso_privacy, consenso_cookie, ip_address, user_agent, 
             hash_consenso, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            nome, cognome, indirizzo, cap, citta, provincia, telefono or "",
            1 if consenso_privacy == "on" else 0,
            1 if consenso_cookie == "on" else 0,
            ip, user_agent, hash_consenso, timestamp
        ))
        consenso_id = c.lastrowid
        conn.commit()
        conn.close()
        
        # Risposta
        indirizzo_completo = f"{indirizzo}, {cap} {citta} ({provincia})"
        
        return {
            "successo": True,
            "messaggio": "✅ Consenso registrato con successo!",
            "riepilogo": {
                "id": f"CONS-{consenso_id:06d}",
                "nome_completo": f"{nome} {cognome}",
                "indirizzo_completo": indirizzo_completo,
                "telefono": telefono or "Non fornito",
                "ip_autenticazione": ip,
                "timestamp": timestamp,
                "hash_consenso": hash_consenso
            }
        }
        
    except Exception as e:
        print(f"❌ Errore consenso: {e}")
        return JSONResponse(
            status_code=500,
            content={"errore": f"Errore interno: {str(e)}"}
        )

@app.get("/api/health")
async def health():
    """Health check"""
    return {
        "service": "consenso-gdpr",
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }

@app.on_event("startup")
async def startup():
    init_db()
    print(f"🚀 Consenso API avviata su porta {PORT}")

# === MAIN ===
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT)
