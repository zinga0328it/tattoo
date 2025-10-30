#!/usr/bin/env python3
"""
API Gallery per Roma Studio Tattoo
Legge direttamente dal database SQLite e genera JSON per il sito web
SICURO: posizionato fuori dalla directory pubblica
"""

import sqlite3
import json
import os
from datetime import datetime
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

# Configurazione
DB_FILE = "/home/alex/web/tatuaggi/tattoo_gallery.db"
IMAGE_DIR = "/var/www/romastudiotattoo/images"

app = Flask(__name__)
CORS(app)  # Permetti richieste cross-origin

def get_tattoos_from_db():
    """Ottiene i tatuaggi dal database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, description, filename, uploaded_at
            FROM tattoos
            ORDER BY uploaded_at DESC
        ''')
        
        tattoos = cursor.fetchall()
        conn.close()
        
        result = []
        for tattoo in tattoos:
            tattoo_id, username, description, filename, uploaded_at = tattoo
            
            # Verifica che il file esista
            file_path = os.path.join(IMAGE_DIR, filename)
            if os.path.exists(file_path):
                result.append({
                    "id": tattoo_id,
                    "username": username,
                    "description": description,
                    "filename": filename,
                    "uploaded_at": uploaded_at,
                    "image_url": f"/images/{filename}"
                })
        
        return result
    except Exception as e:
        print(f"Errore nel recupero dal database: {e}")
        return []

@app.route('/api/tattoos')
def api_tattoos():
    """API endpoint per ottenere tutti i tatuaggi"""
    tattoos = get_tattoos_from_db()
    return jsonify({
        "success": True,
        "total": len(tattoos),
        "generated_at": datetime.now().isoformat(),
        "tattoos": tattoos
    })

@app.route('/api/stats')
def api_stats():
    """API endpoint per statistiche"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM tattoos")
        total_tattoos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT username) FROM tattoos")
        unique_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT uploaded_at FROM tattoos ORDER BY uploaded_at DESC LIMIT 1")
        last_upload = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            "success": True,
            "total_tattoos": total_tattoos,
            "unique_users": unique_users,
            "last_upload": last_upload[0] if last_upload else None,
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/images/<filename>')
def serve_image(filename):
    """Serve le immagini"""
    return send_from_directory(IMAGE_DIR, filename)

@app.route('/')
def index():
    """Pagina principale"""
    return """
    <h1>Roma Studio Tattoo - API Gallery</h1>
    <p>Endpoints disponibili:</p>
    <ul>
        <li><a href="/api/tattoos">/api/tattoos</a> - Lista tutti i tatuaggi</li>
        <li><a href="/api/stats">/api/stats</a> - Statistiche</li>
        <li>/images/&lt;filename&gt; - Serve le immagini</li>
    </ul>
    """

if __name__ == '__main__':
    print("🚀 Avvio API Gallery Roma Studio Tattoo")
    print(f"📂 Database: {DB_FILE}")
    print(f"🖼️ Immagini: {IMAGE_DIR}")
    app.run(host='0.0.0.0', port=5000, debug=False)
