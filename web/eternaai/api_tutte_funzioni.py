from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import List
import time

app = FastAPI()

# --- Funzione 1: Diagramma (placeholder, non genera PNG via API) ---
@app.get("/1")
def diagramma():
    return {"msg": "Funzione diagramma chiamata (solo esempio, non genera PNG via API)"}

# --- Funzione 2: Colonna con più numeri pari ---
class MatriceInput(BaseModel):
    matrice: List[List[int]]

@app.post("/2")
def colonna_pari(data: MatriceInput):
    matrice = data.matrice
    best_count = -1
    best_col = -1
    dettagli = []
    for col in range(len(matrice[0])):
        count = 0
        colonna = [matrice[riga][col] for riga in range(len(matrice))]
        for val in colonna:
            if val % 2 == 0:
                count += 1
        dettagli.append({"colonna": col, "valori": colonna, "pari": count})
        if count > best_count:
            best_count = count
            best_col = col
    return {"colonna_migliore": best_col, "dettagli": dettagli}

# --- Funzione 3: Rate limit ---
RATE_LIMIT = 10
WINDOW = 60
rate_table = {}

@app.get("/3")
def test_endpoint(request: Request):
    ip = request.client.host
    now = int(time.time())
    window = now // WINDOW
    key = f"{ip}:{window}"
    count = rate_table.get(key, 0)
    if count >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Troppo traffico, riprova più tardi.")
    rate_table[key] = count + 1
    return {"msg": "Richiesta accettata"}

# Puoi aggiungere altre funzioni /4 /5 /6 /7 qui seguendo lo stesso schema!
