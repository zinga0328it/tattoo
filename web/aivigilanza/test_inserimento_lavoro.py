#!/usr/bin/env python3
"""
Script di test per inserire lavori FTTH via Yggdrasil
Uso: python3 test_inserimento_lavoro.py
"""

import requests
import json

# Configurazione Yggdrasil
BACKEND_URL = "http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:6030"
API_KEY = "JHzxUzdAK8LJ33Y50MDgLf5E62flYset4MYA6ELpXpU="

def inserisci_lavoro_test():
    """Inserisce un lavoro di test nel database"""

    work_data = {
        "numero_wr": "WR-GPT-001",
        "nome_cliente": "Mario Rossi",
        "indirizzo": "Via Roma 123, Milano",
        "operatore": "Tecnico A",
        "tipo_lavoro": "Installazione FTTH",
        "telefono_cliente": "3331234567",
        "note": "Installazione urgente inserita dal GPT",
        "extra_fields": {
            "priorita": "alta",
            "data_appuntamento": "2025-01-15"
        }
    }

    try:
        print("🚀 Inserimento lavoro di test...")
        print(f"📍 Endpoint: {BACKEND_URL}/manual/works")
        print(f"📊 Dati: {json.dumps(work_data, indent=2)}")
        print()

        response = requests.post(
            f"{BACKEND_URL}/manual/works",
            json=work_data,
            headers={"X-API-Key": API_KEY},
            timeout=10
        )

        print(f"📡 Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Lavoro inserito con successo!")
            print(f"🆔 ID: {result.get('id')}")
            print(f"📋 WR: {result.get('numero_wr')}")
            return True
        else:
            print(f"❌ Errore: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Errore connessione: {e}")
        return False

def verifica_lavoro_inserito():
    """Verifica che il lavoro sia presente nel database"""
    try:
        print("\n🔍 Verifica lavoro nel database...")

        response = requests.get(
            f"{BACKEND_URL}/works/",
            headers={"X-API-Key": API_KEY},
            timeout=10
        )

        if response.status_code == 200:
            works = response.json()
            gpt_work = next((w for w in works if w['numero_wr'] == 'WR-GPT-001'), None)

            if gpt_work:
                print("✅ Lavoro trovato nel database!")
                print(f"📊 Stato: {gpt_work.get('stato')}")
                print(f"👤 Cliente: {gpt_work.get('nome_cliente')}")
                print(f"📍 Indirizzo: {gpt_work.get('indirizzo')}")
                return True
            else:
                print("❌ Lavoro non trovato nel database")
                return False
        else:
            print(f"❌ Errore lettura database: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Errore verifica: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test Inserimento Lavoro FTTH via Yggdrasil")
    print("=" * 50)

    # Test inserimento
    success = inserisci_lavoro_test()

    if success:
        # Verifica che sia nel database
        verifica_lavoro_inserito()

        print("\n🎉 Test completato con successo!")
        print("Il GPT può ora inserire lavori nel database FTTH! 🤖")
    else:
        print("\n❌ Test fallito - controllare la connessione Yggdrasil")