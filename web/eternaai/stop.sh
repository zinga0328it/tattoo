#!/bin/bash



# Ferma il processo uvicorn della nuova API sulla porta 1024
sudo pkill -f "uvicorn api_tutte_funzioni:app --port 1024"

echo "Tutte le API FastAPI sono state fermate!"
