#!/usr/bin/env python3
"""
Script per scaricare tutti i lavori FTTH dal backend remoto via Yggdrasil.
Uso: python3 scarica_lavori_remoto.py [output_file.json]
"""

import sys
import json
import requests
from datetime import datetime

# Configurazione backend Yggdrasil
BACKEND_URL = "http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:6030"
API_KEY = "JHzxUzdAK8LJ33Y50MDgLf5E62flYset4MYA6ELpXpU="

def scarica_lavori():
    """Scarica tutti i lavori dal backend FTTH"""
    url = f"{BACKEND_URL}/works/"
    headers = {"X-API-Key": API_KEY}

    try:
        print(f"📡 Connessione a {url}...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        lavori = response.json()
        print(f"✅ Scaricati {len(lavori)} lavori")

        return lavori

    except requests.exceptions.RequestException as e:
        print(f"❌ Errore connessione: {e}")
        return None

def salva_json(dati, filename):
    """Salva i dati in formato JSON"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dati, f, indent=2, ensure_ascii=False)
        print(f"💾 Salvato in {filename}")
    except Exception as e:
        print(f"❌ Errore salvataggio: {e}")

def mostra_statistiche(lavori):
    """Mostra statistiche sui lavori scaricati"""
    if not lavori:
        return

    stati = {}
    operatori = {}
    tecnici = {}

    for lavoro in lavori:
        # Conteggio per stato
        stato = lavoro.get('stato', 'sconosciuto')
        stati[stato] = stati.get(stato, 0) + 1

        # Conteggio per operatore
        operatore = lavoro.get('operatore', 'sconosciuto')
        operatori[operatore] = operatori.get(operatore, 0) + 1

        # Conteggio per tecnico
        tecnico = lavoro.get('tecnico_assegnato')
        if tecnico and isinstance(tecnico, dict):
            nome_tecnico = f"{tecnico.get('nome', '')} {tecnico.get('cognome', '')}".strip()
            if nome_tecnico:
                tecnici[nome_tecnico] = tecnici.get(nome_tecnico, 0) + 1

    print("\n📊 STATISTICHE LAVORI:")
    print(f"   Totale: {len(lavori)}")
    print("   Per stato:")
    for stato, count in stati.items():
        print(f"     {stato}: {count}")

    print("   Per operatore:")
    for operatore, count in operatori.items():
        print(f"     {operatore}: {count}")

    if tecnici:
        print("   Per tecnico:")
        for tecnico, count in tecnici.items():
            print(f"     {tecnico}: {count}")

def main():
    # Determina nome file output
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"lavori_remoti_{timestamp}.json"

    print("🚀 Script download lavori FTTH da Yggdrasil")
    print(f"   Backend: {BACKEND_URL}")
    print(f"   Output: {output_file}")
    print()

    # Scarica i dati
    lavori = scarica_lavori()

    if lavori is not None:
        # Mostra statistiche
        mostra_statistiche(lavori)

        # Salva su file
        salva_json(lavori, output_file)

        print("\n✅ Operazione completata!")
        print(f"   File salvato: {output_file}")
    else:
        print("\n❌ Operazione fallita!")
        sys.exit(1)

if __name__ == "__main__":
    main()