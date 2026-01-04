#!/usr/bin/env python3
"""
Backend Flask per generazione contratti - Porta 5501
Gestisce endpoint:
- /genera-contratto (guardiania)
- /genera-contratto-pulizie (pulizie ordinarie/straordinarie/sanificazione)
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
from datetime import datetime
from io import BytesIO

# Import moduli contratti
from guardiania import genera_contratto_guardiania
from pulizie import genera_contratto_pulizie, TARIFFE
from ricontatti import genera_contratto_ricontatto
import requests

# Telegram per notifiche
TELEGRAM_BOT_TOKEN = "8296100727:AAHVXF0PT9BKown81BuV-jMcYTS7hstTnL8"
TELEGRAM_CHAT_ID = "7586394272"

def send_telegram_notification(message: str):
    """Invia notifica Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=5)
    except Exception as e:
        print(f"Errore Telegram: {e}")

app = Flask(__name__)
CORS(app)

# Cartella per salvare i contratti generati
CONTRATTI_DIR = "/var/www/aivigilanza/contratti"
os.makedirs(CONTRATTI_DIR, exist_ok=True)


@app.route('/genera-contratto', methods=['POST', 'OPTIONS'])
def genera_contratto():
    """
    Endpoint per generare contratto guardiania.
    
    POST JSON:
    {
        "cliente": {
            "nome": "Mario Rossi",
            "indirizzo": "Via Roma 1, 00100 Roma",
            "cf": "RSSMRA80A01H501Z",
            "telefono": "333 1234567",
            "email": "mario@email.it"
        },
        "servizio": {
            "operatori": 10,
            "ore": 1,
            "tariffa": 20.0,
            "data_evento": "2025-01-15",
            "luogo": "Roma"
        }
    }
    """
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Nessun dato ricevuto"}), 400
        
        # Supporta ENTRAMBI i formati:
        # Formato 1 (nuovo): { "cliente": {...}, "servizio": {...} }
        # Formato 2 (frontend attuale): { "numero_operatori": X, "ore_per_operatore": Y, ... }
        
        if 'cliente' in data:
            # Formato nuovo strutturato
            cliente = data.get('cliente', {})
            nome = cliente.get('nome', 'Cliente')
            indirizzo = cliente.get('indirizzo', '')
            cf = cliente.get('cf', '')
            
            servizio = data.get('servizio', {})
            operatori = int(servizio.get('operatori', 1))
            ore = int(servizio.get('ore', 1))
            tariffa = float(servizio.get('tariffa', 20.0))
            data_inizio = servizio.get('data_inizio', servizio.get('data_evento', ''))
            durata = int(servizio.get('durata_giorni', 1))
            luogo = servizio.get('luogo', 'Roma')
        else:
            # Formato frontend attuale (flat)
            nome = data.get('nome_cliente', 'Cliente')
            indirizzo = data.get('indirizzo_cliente', data.get('luogo', ''))
            cf = data.get('cf_cliente', '')
            
            operatori = int(data.get('numero_operatori', 1))
            ore = int(data.get('durata_ore', data.get('ore_per_operatore', 1)))
            tariffa = float(data.get('tariffa_oraria', 20.0))
            data_inizio = data.get('data_inizio', '')
            durata = int(data.get('durata_giorni', 1))
            luogo = data.get('luogo', data.get('foro_competente', 'Roma'))
        
        servizi = data.get('servizi', None)
        
        # Genera nome file unico
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_safe = "".join(c for c in nome if c.isalnum() or c in (' ', '-', '_')).strip()
        nome_safe = nome_safe.replace(' ', '_')[:30]
        filename = f"contratto_guardiania_{nome_safe}_{timestamp}.pdf"
        filepath = os.path.join(CONTRATTI_DIR, filename)
        
        # Genera il contratto PDF
        genera_contratto_guardiania(
            cliente_nome=nome,
            cliente_indirizzo=indirizzo,
            cliente_cf=cf,
            num_operatori=operatori,
            ore_per_operatore=ore,
            tariffa_oraria=tariffa,
            data_inizio=data_inizio if data_inizio else None,
            durata_giorni=durata,
            servizi=servizi,
            luogo=luogo,
            output_path=filepath
        )
        
        # Calcola totale per la risposta
        totale = operatori * ore * tariffa
        
        # Log
        print(f"[{datetime.now()}] Contratto generato: {filename} - Cliente: {nome} - Totale: €{totale:.2f}")
        
        # Restituisci il PDF
        return send_file(
            filepath,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"[{datetime.now()}] ERRORE: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/genera-contratto-pulizie', methods=['POST', 'OPTIONS'])
def genera_contratto_pulizie_endpoint():
    """
    Endpoint per generare contratto pulizie.
    
    POST JSON:
    {
        "nome_cliente": "Mario Rossi",
        "tipo_servizio": "straordinarie",  // ordinarie (€15), straordinarie (€20), sanificazione (€20)
        "numero_operatori": 1,
        "ore_totali": 4,
        "luogo": "Roma",
        "note": ""
    }
    """
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Nessun dato ricevuto"}), 400
        
        # Estrai dati
        nome = data.get('nome_cliente', data.get('nome', 'Cliente'))
        indirizzo = data.get('indirizzo_cliente', data.get('indirizzo', ''))
        cf = data.get('cf_cliente', data.get('cf', ''))
        
        # Tipo servizio e tariffa
        tipo_servizio = data.get('tipo_servizio', 'straordinarie').lower()
        if tipo_servizio not in ['ordinarie', 'straordinarie', 'sanificazione']:
            tipo_servizio = 'straordinarie'
        
        # Parametri
        operatori = int(data.get('numero_operatori', data.get('operatori', 1)))
        ore = int(data.get('ore_totali', data.get('ore', data.get('durata_ore', 4))))
        tariffa = data.get('tariffa_oraria')
        if tariffa:
            tariffa = float(tariffa)
        else:
            tariffa = TARIFFE.get(tipo_servizio, 20.0)
        
        luogo = data.get('luogo', data.get('foro_competente', 'Roma'))
        data_inizio = data.get('data_inizio', '')
        note = data.get('note', '')
        
        # Genera nome file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_safe = "".join(c for c in nome if c.isalnum() or c in (' ', '-', '_')).strip()
        nome_safe = nome_safe.replace(' ', '_')[:30]
        filename = f"contratto_pulizie_{tipo_servizio}_{nome_safe}_{timestamp}.pdf"
        filepath = os.path.join(CONTRATTI_DIR, filename)
        
        # Genera PDF
        genera_contratto_pulizie(
            cliente_nome=nome,
            cliente_indirizzo=indirizzo,
            cliente_cf=cf,
            tipo_servizio=tipo_servizio,
            num_operatori=operatori,
            ore_totali=ore,
            tariffa_oraria=tariffa,
            data_inizio=data_inizio if data_inizio else None,
            luogo=luogo,
            note=note,
            output_path=filepath
        )
        
        # Calcola totale per log
        totale = operatori * ore * tariffa
        print(f"[{datetime.now()}] Contratto pulizie generato: {filename} - Tipo: {tipo_servizio} - Cliente: {nome} - Totale: €{totale:.2f}")
        
        return send_file(
            filepath,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"[{datetime.now()}] ERRORE pulizie: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/genera-contratto-ricontatto', methods=['POST', 'OPTIONS'])
def genera_contratto_ricontatto_endpoint():
    """
    Endpoint per generare contratto ricontatto/consulenza.
    Salva richiesta e genera PDF.
    
    POST JSON:
    {
        "nome": "Mario",
        "cognome": "Rossi",
        "email": "mario@email.it",
        "telefono": "333 1234567",
        "indirizzo": "Via Roma 1",
        "citta": "Roma",
        "cap": "00100",
        "cf_piva": "RSSMRA80A01H501Z",
        "tipo_servizio": "vigilanza",
        "descrizione_richiesta": "Vorrei info...",
        "privacy_accettata": true,
        "contratto_accettato": true
    }
    """
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Nessun dato ricevuto"}), 400
        
        # Campi obbligatori
        nome = data.get('nome', '').strip()
        cognome = data.get('cognome', '').strip()
        email = data.get('email', '').strip()
        
        if not nome or not cognome or not email:
            return jsonify({"error": "Nome, cognome e email sono obbligatori"}), 400
        
        # Verifica accettazioni
        if not data.get('privacy_accettata'):
            return jsonify({"error": "Devi accettare l'informativa privacy"}), 400
        if not data.get('contratto_accettato'):
            return jsonify({"error": "Devi accettare il contratto di ricontatto"}), 400
        
        # Dati opzionali
        telefono = data.get('telefono', '')
        indirizzo = data.get('indirizzo', '')
        citta = data.get('citta', '')
        cap = data.get('cap', '')
        cf_piva = data.get('cf_piva', '')
        tipo_servizio = data.get('tipo_servizio', '')
        descrizione = data.get('descrizione_richiesta', '')
        
        # Genera nome file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_safe = f"{nome}_{cognome}".replace(' ', '_')[:30]
        nome_safe = "".join(c for c in nome_safe if c.isalnum() or c == '_')
        filename = f"ricontatto_{nome_safe}_{timestamp}.pdf"
        filepath = os.path.join(CONTRATTI_DIR, filename)
        
        # Genera PDF
        genera_contratto_ricontatto(
            nome=nome,
            cognome=cognome,
            email=email,
            telefono=telefono,
            indirizzo=indirizzo,
            citta=citta,
            cap=cap,
            cf_piva=cf_piva,
            tipo_servizio=tipo_servizio,
            descrizione_richiesta=descrizione,
            output_path=filepath
        )
        
        # Mappa tipo servizio
        tipi = {
            "vigilanza": "🛡️ Vigilanza Privata",
            "pulizie": "🧹 Pulizie Professionali",
            "sicurezza": "🔐 Consulenza Sicurezza",
            "web": "🌐 Servizi Web",
            "altro": "📋 Altro"
        }
        servizio_desc = tipi.get(tipo_servizio, tipo_servizio or "Non specificato")
        
        # Invia notifica Telegram
        msg = (
            f"🔔 <b>NUOVA RICHIESTA DI RICONTATTO</b>\n\n"
            f"👤 <b>{nome} {cognome}</b>\n"
            f"📧 {email}\n"
            f"📞 {telefono or 'Non fornito'}\n"
            f"📍 {indirizzo}, {cap} {citta}\n\n"
            f"🎯 <b>Servizio:</b> {servizio_desc}\n"
            f"📝 <b>Richiesta:</b>\n{descrizione or 'Nessuna descrizione'}\n\n"
            f"✅ Privacy e contratto accettati"
        )
        send_telegram_notification(msg)
        
        # Log
        print(f"[{datetime.now()}] Ricontatto: {nome} {cognome} - {email} - {tipo_servizio}")
        
        # Restituisci PDF
        return send_file(
            filepath,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"[{datetime.now()}] ERRORE ricontatto: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "contratti-guardiania",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/info', methods=['GET'])
def info():
    """Info sul servizio."""
    return jsonify({
        "service": "Generatore Contratti Servicess.net",
        "version": "2.0.0",
        "endpoints": {
            "/genera-contratto": "POST - Genera contratto guardiania PDF",
            "/genera-contratto-pulizie": "POST - Genera contratto pulizie PDF",
            "/api/health": "GET - Health check",
            "/api/info": "GET - Info servizio"
        },
        "tariffe_pulizie": {
            "ordinarie": "€15/ora",
            "straordinarie": "€20/ora",
            "sanificazione": "€20/ora"
        }
    })


if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Backend Contratti Servicess.net")
    print("   Porta: 5501")
    print("   Endpoints:")
    print("   - /genera-contratto (guardiania)")
    print("   - /genera-contratto-pulizie (pulizie)")
    print("=" * 50)
    
    app.run(
        host='127.0.0.1',
        port=5501,
        debug=False,
        threaded=True
    )
