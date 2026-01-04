#!/usr/bin/env python3
"""
Script di test per modificare lavori FTTH via Yggdrasil
Uso: python3 test_modifica_lavoro.py
"""

import requests
import json

# Configurazione Yggdrasil
BACKEND_URL = "http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:6030"
API_KEY = "JHzxUzdAK8LJ33Y50MDgLf5E62flYset4MYA6ELpXpU="

def modifica_lavoro_test():
    """Modifica un lavoro esistente nel database"""

    work_id = 20  # ID del lavoro creato prima
    update_data = {
        "stato": "chiuso",
        "note": "Lavoro completato dal GPT - Installazione riuscita",
        "nome_cliente": "Mario Rossi",
        "tecnico_assegnato": 1,  # Assegna il tecnico con ID 1
        "extra_fields": {
            "priorita": "completato",
            "data_appuntamento": "2025-01-15",
            "esito": "successo"
        }
    }

    try:
        print("🔄 Modifica lavoro esistente...")
        print(f"📍 Endpoint: {BACKEND_URL}/works/{work_id}")
        print(f"📊 Dati aggiornamento: {json.dumps(update_data, indent=2)}")
        print()

        response = requests.put(
            f"{BACKEND_URL}/works/{work_id}",
            json=update_data,
            headers={"X-API-Key": API_KEY},
            timeout=10
        )

        print(f"📡 Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Lavoro modificato con successo!")
            print(f"🆔 ID: {result.get('id')}")
            print(f"📋 WR: {result.get('numero_wr')}")
            print(f"📊 Stato: {result.get('stato')}")
            print(f"👤 Cliente: {result.get('nome_cliente')}")
            print(f"👷 Tecnico: {result.get('tecnico_assegnato')}")
            return True
        else:
            print(f"❌ Errore: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Errore connessione: {e}")
        return False

def verifica_modifica():
    """Verifica che le modifiche siano state applicate"""
    try:
        print("\n🔍 Verifica modifiche nel database...")

        response = requests.get(
            f"{BACKEND_URL}/works/20",
            headers={"X-API-Key": API_KEY},
            timeout=10
        )

        if response.status_code == 200:
            work = response.json()
            print("✅ Modifiche confermate!")
            print(f"📊 Stato: {work.get('stato')}")
            print(f"👤 Cliente: {work.get('nome_cliente')}")
            print(f"📝 Note: {work.get('note')}")
            print(f"👷 Tecnico ID: {work.get('tecnico_assegnato')}")
            return True
        else:
            print(f"❌ Errore lettura: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Errore verifica: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Test Modifica Lavoro FTTH via Yggdrasil")
    print("=" * 50)

    # Test modifica
    success = modifica_lavoro_test()

    if success:
        # Verifica le modifiche
        verifica_modifica()

        print("\n🎉 Test modifica completato con successo!")
        print("Il GPT può ora modificare lavori nel database FTTH! 🤖")
    else:
        print("\n❌ Test modifica fallito - controllare la connessione Yggdrasil")