#!/usr/bin/env python3
"""
carrello.py - Backend Carrello Consegne con Telegram Bot
Servicess.net - Sistema ordini e consegne

Porta: 5504 (HTTPS)
Endpoints:
- /api/prodotti (GET) - Lista prodotti
- /api/ordine (POST) - Crea ordine
- /api/gestionale/ordini (GET) - Lista ordini (protetto)
- /api/gestionale/ordine/<id>/stato (PUT) - Aggiorna stato (protetto)
- /api/gestionale/utenti (GET) - Lista utenti (protetto)
- /api/gestionale/utente/<tel>/ban (POST) - Ban/Unban utente (protetto)
- /api/telegram/webhook (POST) - Webhook Telegram
"""

import os
import ssl
import json
import sqlite3
import secrets
import asyncio
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import Flask, request, jsonify, g
from flask_cors import CORS
import requests
from dotenv import load_dotenv

# Carica variabili ambiente
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ============== CONFIGURAZIONE ==============
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8296100727:AAHVXF0PT9BKown81BuV-jMcYTS7hstTnL8')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
API_KEY = os.getenv('API_KEY', secrets.token_urlsafe(32))
DB_PATH = os.getenv('DB_PATH', 'ordini.db')
HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 5504))
SSL_CERT = os.getenv('SSL_CERT')
SSL_KEY = os.getenv('SSL_KEY')

# Chat IDs autorizzati per ricevere notifiche (si popolano automaticamente)
AUTHORIZED_CHATS = set()

print(f"🔧 Configurazione:")
print(f"   - Telegram Bot: {'✅' if TELEGRAM_BOT_TOKEN else '❌'}")
print(f"   - API Key: {API_KEY[:10]}...")
print(f"   - Database: {DB_PATH}")


# ============== DATABASE ==============
def get_db():
    """Ottiene connessione database."""
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    """Chiude connessione database."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Inizializza database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabella ordini
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ordini (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codice_conferma TEXT UNIQUE NOT NULL,
            telefono TEXT NOT NULL,
            indirizzo_consegna TEXT NOT NULL,
            prodotti TEXT NOT NULL,
            totale REAL NOT NULL,
            stato TEXT DEFAULT 'in_attesa',
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabella utenti
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS utenti (
            telefono TEXT PRIMARY KEY,
            nome TEXT,
            ordini_totali INTEGER DEFAULT 0,
            ordini_completati INTEGER DEFAULT 0,
            ordini_cancellati INTEGER DEFAULT 0,
            valutazione REAL DEFAULT 5.0,
            banned INTEGER DEFAULT 0,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_order_at TIMESTAMP
        )
    ''')
    
    # Tabella prodotti
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prodotti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descrizione TEXT,
            prezzo REAL NOT NULL,
            immagine TEXT DEFAULT '📦',
            categoria TEXT DEFAULT 'altro',
            disponibile INTEGER DEFAULT 1
        )
    ''')
    
    # Tabella chat Telegram autorizzate
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telegram_chats (
            chat_id TEXT PRIMARY KEY,
            username TEXT,
            authorized INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Inserisci prodotti di esempio se tabella vuota
    cursor.execute('SELECT COUNT(*) FROM prodotti')
    if cursor.fetchone()[0] == 0:
        prodotti_esempio = [
            ('Margherita', 'Pizza classica con mozzarella e basilico', 8.50, '🍕', 'cibo'),
            ('Diavola', 'Pizza piccante con salame piccante', 9.50, '🌶️', 'cibo'),
            ('Quattro Formaggi', 'Pizza con 4 tipi di formaggio', 10.00, '🧀', 'cibo'),
            ('Coca Cola', 'Bibita gassata 33cl', 2.50, '🥤', 'bevande'),
            ('Acqua Naturale', 'Acqua minerale 50cl', 1.00, '💧', 'bevande'),
            ('Birra Peroni', 'Birra chiara 33cl', 3.00, '🍺', 'bevande'),
            ('Tiramisù', 'Dolce al mascarpone con savoiardi', 4.00, '🍰', 'dolci'),
            ('Cannolo Siciliano', 'Dolce ripieno di ricotta', 3.50, '🥮', 'dolci'),
            ('Legna da Ardere', 'Fascio di legna secca 10kg', 8.00, '🪵', 'combustibili'),
            ('Pellet Premium', 'Sacco pellet 15kg certificato', 6.50, '🔥', 'combustibili'),
        ]
        cursor.executemany(
            'INSERT INTO prodotti (nome, descrizione, prezzo, immagine, categoria) VALUES (?, ?, ?, ?, ?)',
            prodotti_esempio
        )
    
    conn.commit()
    conn.close()
    print("✅ Database inizializzato")


# ============== SICUREZZA ==============
def require_api_key(f):
    """Decorator per richiedere API Key."""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('x-api-key') or request.headers.get('X-API-Key')
        if not api_key or api_key != API_KEY:
            return jsonify({'error': 'API Key non valida o mancante'}), 401
        return f(*args, **kwargs)
    return decorated


# ============== TELEGRAM BOT ==============
def send_telegram_message(text, chat_id=None, reply_markup=None):
    """Invia messaggio Telegram con bottoni opzionali."""
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ Telegram Bot Token non configurato")
        return False
    
    # Se chat_id non specificato, usa chat autorizzati o chat di default
    if chat_id:
        target_chats = [chat_id]
    elif AUTHORIZED_CHATS:
        target_chats = list(AUTHORIZED_CHATS)
    elif TELEGRAM_CHAT_ID:
        target_chats = [TELEGRAM_CHAT_ID]
    else:
        print("⚠️ Nessuna chat Telegram configurata")
        return False
    
    success = False
    for cid in target_chats:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                'chat_id': cid,
                'text': text,
                'parse_mode': 'HTML'
            }
            if reply_markup:
                payload['reply_markup'] = json.dumps(reply_markup)
            
            response = requests.post(url, json=payload, timeout=10)
            if response.ok:
                success = True
                print(f"✅ Messaggio Telegram inviato a {cid}")
            else:
                print(f"❌ Errore Telegram {cid}: {response.text}")
        except Exception as e:
            print(f"❌ Errore invio Telegram: {e}")
    
    return success


def get_rating_keyboard(telefono):
    """Genera tastiera inline per valutazione cliente."""
    return {
        'inline_keyboard': [
            [
                {'text': '⭐', 'callback_data': f'rate_{telefono}_1'},
                {'text': '⭐⭐', 'callback_data': f'rate_{telefono}_2'},
                {'text': '⭐⭐⭐', 'callback_data': f'rate_{telefono}_3'},
                {'text': '⭐⭐⭐⭐', 'callback_data': f'rate_{telefono}_4'},
                {'text': '⭐⭐⭐⭐⭐', 'callback_data': f'rate_{telefono}_5'}
            ],
            [
                {'text': '🚫 Banna Cliente', 'callback_data': f'ban_{telefono}'}
            ]
        ]
    }


def answer_callback(callback_id, text):
    """Risponde a un callback query di Telegram."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
        requests.post(url, json={
            'callback_query_id': callback_id,
            'text': text,
            'show_alert': False
        }, timeout=5)
    except Exception as e:
        print(f"❌ Errore answer callback: {e}")


def genera_codice_conferma():
    """Genera codice conferma univoco."""
    return 'ORD' + secrets.token_hex(4).upper()


# ============== ENDPOINTS PUBBLICI ==============

@app.route('/api/prodotti', methods=['GET'])
def get_prodotti():
    """Lista prodotti disponibili."""
    try:
        db = get_db()
        cursor = db.execute(
            'SELECT id, nome, descrizione, prezzo, immagine, categoria FROM prodotti WHERE disponibile = 1'
        )
        prodotti = [dict(row) for row in cursor.fetchall()]
        return jsonify(prodotti)
    except Exception as e:
        print(f"❌ Errore prodotti: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ordine', methods=['POST', 'OPTIONS'])
def crea_ordine():
    """Crea nuovo ordine."""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        telefono = data.get('telefono', '').strip()
        prodotti = data.get('prodotti', [])
        indirizzo = data.get('indirizzo_consegna', '').strip()
        note = data.get('note', '').strip()
        
        # Validazione
        if not telefono:
            return jsonify({'error': 'Numero di telefono obbligatorio'}), 400
        if not prodotti:
            return jsonify({'error': 'Carrello vuoto'}), 400
        if not indirizzo:
            return jsonify({'error': 'Indirizzo di consegna obbligatorio'}), 400
        
        # Controlla se utente bannato
        db = get_db()
        utente = db.execute('SELECT banned FROM utenti WHERE telefono = ?', (telefono,)).fetchone()
        if utente and utente['banned']:
            return jsonify({'error': 'Utente non autorizzato a effettuare ordini'}), 403
        
        # Calcola totale
        totale = sum(p.get('prezzo', 0) * p.get('quantita', 1) for p in prodotti)
        
        # Genera codice conferma
        codice = genera_codice_conferma()
        
        # Salva ordine
        db.execute('''
            INSERT INTO ordini (codice_conferma, telefono, indirizzo_consegna, prodotti, totale, note)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (codice, telefono, indirizzo, json.dumps(prodotti), totale, note))
        
        # Aggiorna/crea utente
        db.execute('''
            INSERT INTO utenti (telefono, ordini_totali, last_order_at)
            VALUES (?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(telefono) DO UPDATE SET
                ordini_totali = ordini_totali + 1,
                last_order_at = CURRENT_TIMESTAMP
        ''', (telefono,))
        
        db.commit()
        
        # Recupera info utente per messaggio Telegram
        utente_info = db.execute('''
            SELECT valutazione, ordini_totali, ordini_completati, ordini_cancellati, note 
            FROM utenti WHERE telefono = ?
        ''', (telefono,)).fetchone()
        
        # Genera stelle valutazione
        if utente_info:
            val = utente_info['valutazione'] or 5
            stelle_piene = int(val)
            stelle_vuote = 5 - stelle_piene
            stelle = '⭐' * stelle_piene + '☆' * stelle_vuote
            ordini_tot = utente_info['ordini_totali'] or 1
            ordini_ok = utente_info['ordini_completati'] or 0
            ordini_canc = utente_info['ordini_cancellati'] or 0
            note_utente = utente_info['note'] or ''
        else:
            stelle = '⭐⭐⭐⭐⭐'
            ordini_tot = 1
            ordini_ok = 0
            ordini_canc = 0
            note_utente = ''
        
        # Avviso cliente problematico
        avviso_cliente = ''
        if ordini_canc > 0:
            avviso_cliente = f'\n\n⚠️ <b>ATTENZIONE:</b> Cliente con {ordini_canc} ordini cancellati!'
        if note_utente:
            avviso_cliente += f'\n📌 <b>Note cliente:</b> {note_utente}'
        if ordini_canc >= 3:
            avviso_cliente = f'\n\n🚨 <b>CLIENTE PROBLEMATICO!</b> {ordini_canc} cancellazioni su {ordini_tot} ordini!'
            if note_utente:
                avviso_cliente += f'\n📌 {note_utente}'
        
        # Notifica Telegram
        prodotti_text = '\n'.join([f"  • {p.get('quantita', 1)}x {p.get('nome', '?')} - €{p.get('prezzo', 0):.2f}" for p in prodotti])
        telegram_msg = f"""🛒 <b>NUOVO ORDINE!</b>

━━━━━━━━━━━━━━━━━━━━
📋 <b>Codice:</b> <code>{codice}</code>
━━━━━━━━━━━━━━━━━━━━

� <b>CLIENTE</b>
📱 Telefono: <code>{telefono}</code>
{stelle} ({val:.1f}/5)
📊 Ordini: {ordini_tot} totali | ✅ {ordini_ok} ok | ❌ {ordini_canc} canc.

🏠 <b>CONSEGNA</b>
{indirizzo}

🛍️ <b>PRODOTTI</b>
{prodotti_text}

━━━━━━━━━━━━━━━━━━━━
💰 <b>TOTALE: €{totale:.2f}</b>
━━━━━━━━━━━━━━━━━━━━

📝 Note: {note if note else '—'}{avviso_cliente}

⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}

👇 <b>Valuta questo cliente:</b>"""
        
        # Invia con bottoni di valutazione
        rating_keyboard = get_rating_keyboard(telefono)
        send_telegram_message(telegram_msg, reply_markup=rating_keyboard)
        
        print(f"✅ Ordine creato: {codice} - Tel: {telefono} - Totale: €{totale:.2f}")
        
        return jsonify({
            'success': True,
            'codice_conferma': codice,
            'totale': totale,
            'messaggio': f'Ordine {codice} creato! Riceverai conferma via SMS.'
        })
        
    except Exception as e:
        print(f"❌ Errore creazione ordine: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ============== ENDPOINTS GESTIONALE (PROTETTI) ==============

@app.route('/api/gestionale/ordini', methods=['GET'])
@require_api_key
def get_ordini():
    """Lista tutti gli ordini con statistiche."""
    try:
        db = get_db()
        stato = request.args.get('stato')
        
        if stato:
            cursor = db.execute(
                'SELECT * FROM ordini WHERE stato = ? ORDER BY created_at DESC',
                (stato,)
            )
        else:
            cursor = db.execute('SELECT * FROM ordini ORDER BY created_at DESC')
        
        ordini = []
        for row in cursor.fetchall():
            ordine = dict(row)
            # prodotti è già JSON string, lo teniamo così per il frontend
            ordini.append(ordine)
        
        # Calcola statistiche
        stats = {
            'in_attesa': len([o for o in ordini if o['stato'] == 'in_attesa']),
            'confermato': len([o for o in ordini if o['stato'] == 'confermato']),
            'in_consegna': len([o for o in ordini if o['stato'] == 'in_consegna']),
            'consegnato': len([o for o in ordini if o['stato'] == 'consegnato']),
            'cancellato': len([o for o in ordini if o['stato'] == 'cancellato']),
        }
        
        return jsonify({
            'ordini': ordini,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/gestionale/valutazioni', methods=['GET'])
@require_api_key
def get_valutazioni():
    """Lista valutazioni clienti."""
    try:
        db = get_db()
        cursor = db.execute('SELECT * FROM utenti ORDER BY valutazione DESC')
        
        valutazioni = {}
        for row in cursor.fetchall():
            utente = dict(row)
            telefono = utente['telefono']
            
            # Trova ultimo ordine
            ultimo_ordine = db.execute(
                'SELECT id FROM ordini WHERE telefono = ? ORDER BY created_at DESC LIMIT 1',
                (telefono,)
            ).fetchone()
            
            valutazioni[telefono] = {
                'valutazione': int(utente.get('valutazione', 5)),
                'ultimo_ordine_id': ultimo_ordine['id'] if ultimo_ordine else None,
                'updated_at': utente.get('last_order_at', '')
            }
        
        return jsonify({
            'valutazioni': valutazioni
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/gestionale/ordine/<int:ordine_id>/stato', methods=['PUT'])
@require_api_key
def aggiorna_stato_ordine(ordine_id):
    """Aggiorna stato ordine."""
    try:
        data = request.get_json()
        nuovo_stato = data.get('stato')
        
        stati_validi = ['in_attesa', 'confermato', 'in_consegna', 'consegnato', 'cancellato']
        if nuovo_stato not in stati_validi:
            return jsonify({'error': f'Stato non valido. Validi: {stati_validi}'}), 400
        
        db = get_db()
        
        # Ottieni ordine
        ordine = db.execute('SELECT * FROM ordini WHERE id = ?', (ordine_id,)).fetchone()
        if not ordine:
            return jsonify({'error': 'Ordine non trovato'}), 404
        
        # Aggiorna stato
        db.execute(
            'UPDATE ordini SET stato = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (nuovo_stato, ordine_id)
        )
        
        # Aggiorna statistiche utente
        telefono = ordine['telefono']
        if nuovo_stato == 'consegnato':
            db.execute(
                'UPDATE utenti SET ordini_completati = ordini_completati + 1 WHERE telefono = ?',
                (telefono,)
            )
        elif nuovo_stato == 'cancellato':
            db.execute(
                'UPDATE utenti SET ordini_cancellati = ordini_cancellati + 1 WHERE telefono = ?',
                (telefono,)
            )
            # Ricalcola valutazione (penalità per cancellazioni)
            db.execute('''
                UPDATE utenti SET valutazione = 
                    CASE 
                        WHEN ordini_totali > 0 THEN 
                            MAX(1, 5 - (ordini_cancellati * 1.0 / ordini_totali) * 4)
                        ELSE 5 
                    END
                WHERE telefono = ?
            ''', (telefono,))
        
        db.commit()
        
        # Notifica Telegram
        stati_emoji = {
            'confermato': '✅',
            'in_consegna': '🚚',
            'consegnato': '🎉',
            'cancellato': '❌'
        }
        emoji = stati_emoji.get(nuovo_stato, '📋')
        send_telegram_message(f"{emoji} Ordine <b>{ordine['codice_conferma']}</b> → {nuovo_stato.upper()}")
        
        return jsonify({'success': True, 'nuovo_stato': nuovo_stato})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/gestionale/utenti', methods=['GET'])
@require_api_key
def get_utenti():
    """Lista utenti."""
    try:
        db = get_db()
        cursor = db.execute('SELECT * FROM utenti ORDER BY last_order_at DESC')
        utenti = [dict(row) for row in cursor.fetchall()]
        
        # Calcola stats utenti
        stats = {
            'totali': len(utenti),
            'bannati': sum(1 for u in utenti if u.get('banned')),
            'attivi': sum(1 for u in utenti if not u.get('banned'))
        }
        
        return jsonify({
            'success': True,
            'utenti': utenti,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/gestionale/utente/<telefono>/ban', methods=['POST'])
@require_api_key
def toggle_ban_utente(telefono):
    """Ban/Unban utente."""
    try:
        db = get_db()
        
        utente = db.execute('SELECT banned FROM utenti WHERE telefono = ?', (telefono,)).fetchone()
        if not utente:
            return jsonify({'error': 'Utente non trovato'}), 404
        
        nuovo_stato = 0 if utente['banned'] else 1
        db.execute('UPDATE utenti SET banned = ? WHERE telefono = ?', (nuovo_stato, telefono))
        db.commit()
        
        azione = 'bannato' if nuovo_stato else 'sbloccato'
        send_telegram_message(f"🚫 Utente <b>{telefono}</b> {azione}")
        
        return jsonify({'success': True, 'banned': bool(nuovo_stato)})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/gestionale/utente/<telefono>/valutazione', methods=['POST'])
@require_api_key
def aggiorna_valutazione_utente(telefono):
    """Aggiorna valutazione utente (1-5 stelle)."""
    try:
        data = request.get_json()
        nuova_valutazione = data.get('valutazione')
        
        if not nuova_valutazione or not (1 <= int(nuova_valutazione) <= 5):
            return jsonify({'error': 'Valutazione deve essere tra 1 e 5'}), 400
        
        db = get_db()
        
        utente = db.execute('SELECT * FROM utenti WHERE telefono = ?', (telefono,)).fetchone()
        if not utente:
            return jsonify({'error': 'Utente non trovato'}), 404
        
        db.execute('UPDATE utenti SET valutazione = ? WHERE telefono = ?', (int(nuova_valutazione), telefono))
        db.commit()
        
        stelle = '⭐' * int(nuova_valutazione)
        send_telegram_message(f"📝 Valutazione aggiornata\n👤 <b>{telefono}</b>\n{stelle} ({nuova_valutazione}/5)")
        
        return jsonify({'success': True, 'valutazione': int(nuova_valutazione)})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/gestionale/utente/<telefono>/note', methods=['POST'])
@require_api_key
def aggiorna_note_utente(telefono):
    """Aggiorna note utente."""
    try:
        data = request.get_json()
        note = data.get('note', '')
        
        db = get_db()
        
        utente = db.execute('SELECT * FROM utenti WHERE telefono = ?', (telefono,)).fetchone()
        if not utente:
            return jsonify({'error': 'Utente non trovato'}), 404
        
        db.execute('UPDATE utenti SET note = ? WHERE telefono = ?', (note, telefono))
        db.commit()
        
        if note:
            send_telegram_message(f"📌 Note aggiornate per <b>{telefono}</b>:\n{note}")
        
        return jsonify({'success': True, 'note': note})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/gestionale/stats', methods=['GET'])
@require_api_key
def get_stats():
    """Statistiche ordini."""
    try:
        db = get_db()
        
        stats = {}
        
        # Conteggi per stato
        for stato in ['in_attesa', 'confermato', 'in_consegna', 'consegnato', 'cancellato']:
            cursor = db.execute('SELECT COUNT(*) as count FROM ordini WHERE stato = ?', (stato,))
            stats[stato] = cursor.fetchone()['count']
        
        # Totale ordini oggi
        cursor = db.execute('''
            SELECT COUNT(*) as count, COALESCE(SUM(totale), 0) as totale 
            FROM ordini 
            WHERE DATE(created_at) = DATE('now')
        ''')
        oggi = cursor.fetchone()
        stats['ordini_oggi'] = oggi['count']
        stats['incasso_oggi'] = oggi['totale']
        
        # Utenti totali e bannati
        cursor = db.execute('SELECT COUNT(*) as tot, SUM(banned) as ban FROM utenti')
        utenti = cursor.fetchone()
        stats['utenti_totali'] = utenti['tot']
        stats['utenti_bannati'] = utenti['ban'] or 0
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============== TELEGRAM WEBHOOK ==============

@app.route('/api/telegram/webhook', methods=['POST'])
def telegram_webhook():
    """Webhook per ricevere messaggi Telegram."""
    try:
        data = request.get_json()
        
        # Gestione callback da bottoni inline (valutazione, ban)
        if 'callback_query' in data:
            callback = data['callback_query']
            callback_id = callback['id']
            chat_id = str(callback['message']['chat']['id'])
            callback_data = callback.get('data', '')
            
            print(f"📩 Telegram Callback: {callback_data}")
            
            # Callback valutazione: rate_TELEFONO_STELLE
            if callback_data.startswith('rate_'):
                parts = callback_data.split('_')
                if len(parts) == 3:
                    telefono = parts[1]
                    rating = int(parts[2])
                    
                    # Aggiorna valutazione nel database
                    db = get_db()
                    db.execute('UPDATE utenti SET valutazione = ? WHERE telefono = ?', (rating, telefono))
                    db.commit()
                    
                    stelle = '⭐' * rating
                    
                    # Rispondi al callback
                    answer_callback(callback_id, f"✅ Valutazione salvata: {stelle}")
                    
                    # Invia conferma
                    send_telegram_message(
                        f"✅ <b>Valutazione salvata!</b>\n\n"
                        f"👤 Cliente: <code>{telefono}</code>\n"
                        f"⭐ Valutazione: {stelle} ({rating}/5)",
                        chat_id
                    )
            
            # Callback ban: ban_TELEFONO
            elif callback_data.startswith('ban_'):
                telefono = callback_data.replace('ban_', '')
                
                db = get_db()
                utente = db.execute('SELECT banned FROM utenti WHERE telefono = ?', (telefono,)).fetchone()
                
                if utente:
                    nuovo_stato = 0 if utente['banned'] else 1
                    db.execute('UPDATE utenti SET banned = ? WHERE telefono = ?', (nuovo_stato, telefono))
                    db.commit()
                    
                    azione = 'BANNATO 🚫' if nuovo_stato else 'SBANNATO ✅'
                    answer_callback(callback_id, f"Cliente {azione}")
                    
                    send_telegram_message(
                        f"🚫 <b>Cliente {azione}</b>\n\n"
                        f"👤 Telefono: <code>{telefono}</code>",
                        chat_id
                    )
                else:
                    answer_callback(callback_id, "❌ Utente non trovato")
            
            return jsonify({'ok': True})
        
        if 'message' in data:
            message = data['message']
            chat_id = str(message['chat']['id'])
            text = message.get('text', '')
            username = message.get('from', {}).get('username', 'Unknown')
            
            print(f"📩 Telegram: {username} ({chat_id}): {text}")
            
            # Comando /start - registra chat
            if text.startswith('/start'):
                AUTHORIZED_CHATS.add(chat_id)
                
                # Salva nel database
                db = get_db()
                db.execute('''
                    INSERT OR REPLACE INTO telegram_chats (chat_id, username)
                    VALUES (?, ?)
                ''', (chat_id, username))
                db.commit()
                
                send_telegram_message(
                    f"✅ <b>Benvenuto!</b>\n\nChat registrata per ricevere notifiche ordini.\n\n"
                    f"Chat ID: <code>{chat_id}</code>",
                    chat_id
                )
            
            # Comando /ordini - lista ordini in attesa
            elif text.startswith('/ordini'):
                db = get_db()
                cursor = db.execute(
                    "SELECT codice_conferma, telefono, totale, stato FROM ordini WHERE stato IN ('in_attesa', 'confermato', 'in_consegna') ORDER BY created_at DESC LIMIT 10"
                )
                ordini = cursor.fetchall()
                
                if ordini:
                    msg = "📋 <b>Ordini Aperti:</b>\n\n"
                    for o in ordini:
                        msg += f"• <b>{o['codice_conferma']}</b> - {o['telefono']} - €{o['totale']:.2f} ({o['stato']})\n"
                else:
                    msg = "✅ Nessun ordine aperto!"
                
                send_telegram_message(msg, chat_id)
            
            # Comando /stats
            elif text.startswith('/stats'):
                db = get_db()
                cursor = db.execute('''
                    SELECT 
                        COUNT(*) as totali,
                        SUM(CASE WHEN stato = 'consegnato' THEN 1 ELSE 0 END) as consegnati,
                        SUM(CASE WHEN stato = 'in_attesa' THEN 1 ELSE 0 END) as in_attesa,
                        SUM(totale) as incasso_totale
                    FROM ordini
                ''')
                stats = cursor.fetchone()
                
                msg = f"""📊 <b>Statistiche</b>

📦 Ordini totali: {stats['totali']}
✅ Consegnati: {stats['consegnati']}
⏳ In attesa: {stats['in_attesa']}
💰 Incasso totale: €{stats['incasso_totale'] or 0:.2f}"""
                
                send_telegram_message(msg, chat_id)
            
            # Comando /help
            elif text.startswith('/help'):
                send_telegram_message(
                    "🤖 <b>Comandi disponibili:</b>\n\n"
                    "/start - Registra chat per notifiche\n"
                    "/ordini - Mostra ordini aperti\n"
                    "/stats - Statistiche\n"
                    "/help - Questo messaggio",
                    chat_id
                )
        
        return jsonify({'ok': True})
        
    except Exception as e:
        print(f"❌ Errore webhook Telegram: {e}")
        return jsonify({'error': str(e)}), 500


# ============== HEALTH CHECK ==============

@app.route('/api/health', methods=['GET'])
def health():
    """Health check."""
    return jsonify({
        'status': 'ok',
        'service': 'carrello-consegne',
        'telegram': bool(TELEGRAM_BOT_TOKEN),
        'timestamp': datetime.now().isoformat()
    })


# ============== AVVIO ==============

def load_authorized_chats():
    """Carica chat autorizzate dal database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute('SELECT chat_id FROM telegram_chats WHERE authorized = 1')
        for row in cursor.fetchall():
            AUTHORIZED_CHATS.add(row[0])
        conn.close()
        print(f"✅ Caricate {len(AUTHORIZED_CHATS)} chat Telegram autorizzate")
    except Exception as e:
        print(f"⚠️ Errore caricamento chat: {e}")


if __name__ == '__main__':
    print("=" * 50)
    print("🛒 Backend Carrello Consegne")
    print("   Servicess.net")
    print("=" * 50)
    
    # Inizializza database
    init_db()
    
    # Carica chat autorizzate
    load_authorized_chats()
    
    # Configura SSL se disponibile
    ssl_context = None
    if SSL_CERT and SSL_KEY and os.path.exists(SSL_CERT) and os.path.exists(SSL_KEY):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(SSL_CERT, SSL_KEY)
        print(f"🔒 SSL abilitato")
    else:
        print("⚠️ SSL non configurato - usando HTTP")
    
    print(f"🚀 Server in ascolto su {HOST}:{PORT}")
    print("=" * 50)
    
    app.run(
        host=HOST,
        port=PORT,
        ssl_context=ssl_context,
        debug=False,
        threaded=True
    )
