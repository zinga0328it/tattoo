import time
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

# Limite: max 10 richieste per IP ogni 60 secondi
RATE_LIMIT = 10
WINDOW = 60
rate_table = {}

def check_rate_limit(ip):
    now = int(time.time())
    window = now // WINDOW
    key = f"{ip}:{window}"
    count = rate_table.get(key, 0)
    if count >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Troppo traffico, riprova più tardi.")
    rate_table[key] = count + 1

@app.get("/test")
def test_endpoint(request: Request):
    ip = request.client.host
    check_rate_limit(ip)
    return {"msg": "Richiesta accettata"}

# ---
# Risposte alle domande:
# 1. Se un IP supera il limite, riceve errore HTTP 429 e la richiesta viene bloccata.
# 2. Si può adattare la logica usando una chiave API come identificatore invece dell'IP.
# 3. Difendersi da flood/DDoS è importante per evitare che il servizio diventi inutilizzabile o vada in crash.
