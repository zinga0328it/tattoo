#!/usr/bin/env python3
import sqlite3
import json
import re
import os

# Percorsi
DB_FILE = "/home/alex/web/tatuaggi/tattoo_gallery.db"
INDEX_FILE = "/var/www/romastudiotattoo/index.html"

def get_tattoos_from_db():
    """Recupera tutti i tatuaggi dal database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, description, filename, uploaded_at
            FROM tattoos 
            ORDER BY uploaded_at DESC
        """)
        
        tattoos = []
        for row in cursor.fetchall():
            tattoo_id, username, description, filename, uploaded_at = row
            
            # Crea l'oggetto tatuaggio nel formato richiesto
            tattoo = {
                "id": tattoo_id,
                "username": username,
                "description": description,
                "filename": filename,
                "uploaded_at": uploaded_at + "+00:00" if not uploaded_at.endswith("+00:00") else uploaded_at,
                "image_url": f"/images/{filename}",
                "detail_url": f"/detail.html?id={tattoo_id}",
                "telegram_url": f"https://t.me/{username}",
                "seo_title": f"{description} - Roma Studio Tattoo",
                "seo_description": f"Tatuaggio: {description}. Realizzato presso Roma Studio Tattoo Roma. Contatta {username} su Telegram.",
                "keywords": f"tatuaggio, {description.lower()}, roma, studio tattoo, {username}"
            }
            tattoos.append(tattoo)
        
        conn.close()
        return tattoos
        
    except Exception as e:
        print(f"Errore nel recupero dal database: {e}")
        return []

def update_homepage_data():
    """Aggiorna i dati inline nella homepage"""
    try:
        # Recupera i tatuaggi dal database
        tattoos = get_tattoos_from_db()
        if not tattoos:
            print("Nessun tatuaggio trovato nel database")
            return False
        
        # Leggi il file index.html
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Crea il nuovo JSON dei dati
        tattoos_json = json.dumps(tattoos, separators=(',', ':'))
        
        # Pattern per trovare la linea con window.tattoosData
        pattern = r'window\.tattoosData\s*=\s*\[.*?\];'
        replacement = f'window.tattoosData = {tattoos_json};'
        
        # Sostituisci i dati
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        if new_content == content:
            print("Nessuna modifica necessaria o pattern non trovato")
            return False
        
        # Scrivi il file aggiornato usando sudo se necessario
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as temp_file:
            temp_file.write(new_content)
            temp_path = temp_file.name
        
        # Usa sudo per copiare il file
        import subprocess
        result = subprocess.run(['sudo', 'cp', temp_path, INDEX_FILE], capture_output=True)
        os.unlink(temp_path)  # Rimuovi il file temporaneo
        
        if result.returncode != 0:
            raise Exception(f"Errore nel copiare il file: {result.stderr.decode()}")
        
        print(f"Homepage aggiornata con {len(tattoos)} tatuaggi")
        return True
        
    except Exception as e:
        print(f"Errore nell'aggiornamento della homepage: {e}")
        return False

if __name__ == "__main__":
    print("Aggiornamento dati homepage...")
    success = update_homepage_data()
    if success:
        print("✅ Homepage aggiornata con successo!")
    else:
        print("❌ Errore nell'aggiornamento della homepage")
