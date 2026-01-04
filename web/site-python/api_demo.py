from flask import Flask, request, jsonify
from database.database import YggdrasilDatabase
import os
import logging
from dotenv import load_dotenv

# Import classi dipendenti
from .dipendenti import Dipendente, DipendenteA

load_dotenv()

app = Flask(__name__)
db = YggdrasilDatabase()

API_KEY = os.getenv('API_KEY', '16e91aab57262cbc01e89abfb5bfc519496197ea51ee31a00ebf957ff30cff47')  # Cambia con una chiave sicura

# Configura logging per fail2ban
logging.basicConfig(filename='database/flask-api.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

# Lista globale dipendenti (in produzione, integra con YggdrasilDatabase)
dipendenti = []

# Funzione per verificare se la richiesta viene dalla rete Yggdrasil (COMMENTATA PER DEMO PUBBLICA)
# def is_from_ygg_network():
#     client_ip = request.remote_addr
#     try:
#         import ipaddress
#         ip = ipaddress.IPv6Address(client_ip)
#         ygg_network = ipaddress.IPv6Network('200::/8')
#         return ip in ygg_network
#     except:
#         return False  # Se non IPv6 o errore, non autorizzato

@app.before_request
def check_access():
    api_key = request.headers.get('X-API-Key')
    if api_key != API_KEY:
        client_ip = request.remote_addr
        logging.warning(f"Invalid API key attempt from {client_ip}")
        return jsonify({"error": "API key invalida"}), 401
    # COMMENTATO PER DEMO PUBBLICA: if not is_from_ygg_network():
    #     client_ip = request.remote_addr
    #     logging.warning(f"Unauthorized access attempt from {client_ip}")
    #     return jsonify({"error": "Accesso negato: solo dalla rete Yggdrasil"}), 403

@app.route('/api/user/<int:telegram_id>', methods=['GET'])
def get_user(telegram_id):
    payment_status = db.check_payment(telegram_id)
    progress = db.get_user_progress(telegram_id)
    return jsonify({
        "telegram_id": telegram_id,
        "payment_status": payment_status,
        "progress": progress
    })

@app.route('/api/user/<int:telegram_id>/key', methods=['GET'])
def get_user_key(telegram_id):
    key = db.get_user_key(telegram_id)
    if key:
        return jsonify({"key": key})
    return jsonify({"error": "Chiave non disponibile"}), 404

@app.route('/api/user/<int:telegram_id>/progress', methods=['POST'])
def update_progress(telegram_id):
    data = request.json
    level = data.get('level', 0)
    db.update_user_progress(telegram_id, level)
    return jsonify({"status": "Progresso aggiornato"})

@app.route('/api/site/login', methods=['POST'])
def site_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    client_ip = request.remote_addr
    if db.verify_site_user(username, password):
        app.logger.info(f"Successful login for {username} from {client_ip}")
        return jsonify({"login": "success"})
    else:
        logging.warning(f"Failed login attempt for {username} from {client_ip}")
        return jsonify({"login": "failed"}), 401

# Nuove route per dipendenti
@app.route('/api/dipendenti', methods=['GET'])
def get_dipendenti():
    return jsonify([d.to_dict() for d in dipendenti])

@app.route('/api/dipendenti', methods=['POST'])
def add_dipendente():
    data = request.json
    matricola = data.get('matricola')
    stipendio = data.get('stipendio')
    straordinario = data.get('straordinario')
    tipo = data.get('tipo', 'Dipendente')
    if tipo == 'DipendenteA':
        d = DipendenteA(matricola, stipendio, straordinario)
    else:
        d = Dipendente(matricola, stipendio, straordinario)
    dipendenti.append(d)
    return jsonify({"status": "Dipendente aggiunto"})

@app.route('/api/dipendenti/<matricola>', methods=['GET'])
def get_dipendente(matricola):
    for d in dipendenti:
        if d.matricola == matricola:
            return jsonify(d.to_dict())
    return jsonify({"error": "Dipendente non trovato"}), 404

@app.route('/api/dipendenti/<matricola>/paga', methods=['POST'])
def paga_dipendente(matricola):
    data = request.json
    ore = data.get('ore', 0)
    for d in dipendenti:
        if d.matricola == matricola:
            totale = d.paga(ore)
            return jsonify({"stipendio_totale": totale})
    return jsonify({"error": "Dipendente non trovato"}), 404

@app.route('/api/dipendenti/<matricola>/malattia', methods=['POST'])
def add_malattia(matricola):
    data = request.json
    giorni = data.get('giorni', 0)
    for d in dipendenti:
        if d.matricola == matricola and isinstance(d, DipendenteA):
            d.prendi_malattia(giorni)
            return jsonify({"status": "Malattia aggiunta"})
    return jsonify({"error": "Dipendente non trovato o senza gestione malattia"}), 404

if __name__ == '__main__':
    print("Starting API...")
    try:
        # Ascolta su tutte le interfacce, ma limitato dalla rete Ygg (ora pubblico per demo)
        app.run(host='::', port=7123, debug=False)
    except Exception as e:
        print(f"Error starting API: {e}")
        import traceback
        traceback.print_exc()
