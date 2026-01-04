#!/bin/bash

# Attiva il virtual environment
source /home/alex/web/eternaai/venv/bin/activate

# Avvia l'applicazione Flask in background
python3 /home/alex/web/eternaai/app.py &

# Attendi un momento per l'avvio
sleep 2

# Avvia il monitoraggio dei log in background
python3 /home/alex/web/eternaai/monitor_logs.py &

echo "Applicazione avviata. Monitora i log per conferme di login."
echo "Per fermare: ./stop.sh"