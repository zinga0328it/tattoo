#!/usr/bin/env python3
"""
Script di aggiornamento galleria - Roma Studio Tattoo
SICURO: posizionato fuori dalla directory pubblica web
"""

import os
import sqlite3
import json
import logging
from datetime import datetime

# Configurazione percorsi SICURI
DB_FILE = "/home/alex/web/tatuaggi/tattoo_gallery.db"
IMAGE_DIR = "/var/www/romastudiotattoo/images"
OUTPUT_GALLERY_JSON = "/var/www/romastudiotattoo/gallery.json"
OUTPUT_TATTOOS_JSON = "/var/www/romastudiotattoo/tattoos.json"  # Compatibilità con sito esistente
OUTPUT_HTML = "/var/www/romastudiotattoo/gallery.html"

def generate_gallery_json():
    """Genera i file JSON della galleria (entrambi i formati)"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, description, filename, uploaded_at, file_id
            FROM tattoos
            ORDER BY uploaded_at DESC
        ''')
        
        tattoos = cursor.fetchall()
        conn.close()
        
        # Formato 1: gallery.json (nuovo formato)
        gallery_data = {
            "generated_at": datetime.now().isoformat(),
            "total_tattoos": len(tattoos),
            "tattoos": []
        }
        
        # Formato 2: tattoos.json (compatibilità con sito esistente)
        tattoos_array = []
        
        for tattoo in tattoos:
            tattoo_id, username, description, filename, uploaded_at, file_id = tattoo
            
            # Verifica che il file esista fisicamente
            file_path = os.path.join(IMAGE_DIR, filename)
            if os.path.exists(file_path):
                # Formato gallery.json
                gallery_data["tattoos"].append({
                    "id": tattoo_id,
                    "username": username,
                    "description": description,
                    "filename": filename,
                    "uploaded_at": uploaded_at,
                    "image_url": f"images/{filename}"
                })
                
                # Formato tattoos.json (compatibilità)
                safe_description = "".join(c for c in description if c.isprintable()).strip()
                
                # SEO ottimizzato con descrizione utente reale
                seo_title = f"{safe_description} - Roma Studio Tattoo"
                if len(seo_title) > 60:  # Limite Google per title
                    seo_title = f"{safe_description[:50]}... - Roma Studio Tattoo"
                
                seo_description = f"Tatuaggio: {safe_description}. Realizzato presso Roma Studio Tattoo Roma. Galleria tatuaggi artistici e professionali."
                if len(seo_description) > 160:  # Limite Google per description
                    seo_description = f"Tatuaggio: {safe_description[:100]}... Realizzato presso Roma Studio Tattoo Roma."
                
                tattoos_array.append({
                    "id": tattoo_id,
                    "username": username or 'Anonimo',
                    "description": safe_description,
                    "filename": filename,
                    "uploaded_at": uploaded_at,
                    "file_id": file_id or "unknown",
                    "image_url": f"/images/{filename}",
                    "seo_title": seo_title,
                    "seo_description": seo_description,
                    "keywords": f"tatuaggio, {safe_description.lower()}, roma, studio tattoo, arte corporea",
                    "alt_text": f"Tatuaggio {safe_description} - Roma Studio Tattoo"
                })
        
        # Salva gallery.json
        with open(OUTPUT_GALLERY_JSON, 'w', encoding='utf-8') as f:
            json.dump(gallery_data, f, indent=2, ensure_ascii=False)
        
        # Salva tattoos.json (formato compatibile)
        with open(OUTPUT_TATTOOS_JSON, 'w', encoding='utf-8') as f:
            json.dump(tattoos_array, f, indent=2, ensure_ascii=False)
        
        logging.info(f"JSON galleria generati: {len(gallery_data['tattoos'])} foto")
        return True
        
    except Exception as e:
        logging.error(f"Errore nella generazione JSON: {e}")
        return False

def generate_gallery_html():
    """Genera una semplice galleria HTML"""
    try:
        # Leggi il JSON gallery
        with open(OUTPUT_GALLERY_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        html_content = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Galleria Tatuaggi - Roma Studio Tattoo</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .gallery {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .tattoo-card {{ background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .tattoo-image {{ width: 100%; height: 300px; object-fit: cover; }}
        .tattoo-info {{ padding: 15px; }}
        .tattoo-description {{ font-weight: bold; margin-bottom: 5px; }}
        .tattoo-author {{ color: #666; font-size: 0.9em; }}
        .tattoo-date {{ color: #999; font-size: 0.8em; }}
        .stats {{ text-align: center; margin-bottom: 20px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎨 Galleria Tatuaggi - Roma Studio Tattoo</h1>
        <div class="stats">
            <p>📸 {data['total_tattoos']} tatuaggi | 🕒 Aggiornato: {data['generated_at'][:19].replace('T', ' ')}</p>
        </div>
    </div>
    
    <div class="gallery">
"""
        
        for tattoo in data['tattoos']:
            html_content += f"""
        <div class="tattoo-card">
            <img src="{tattoo['image_url']}" alt="{tattoo['description']}" class="tattoo-image">
            <div class="tattoo-info">
                <div class="tattoo-description">{tattoo['description']}</div>
                <div class="tattoo-author">👤 {tattoo['username']}</div>
                <div class="tattoo-date">📅 {tattoo['uploaded_at']}</div>
            </div>
        </div>"""
        
        html_content += """
    </div>
</body>
</html>"""
        
        # Salva l'HTML
        with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logging.info("HTML galleria generato")
        return True
        
    except Exception as e:
        logging.error(f"Errore nella generazione HTML: {e}")
        return False

def main():
    """Funzione principale"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("🔄 Aggiornamento galleria in corso...")
    
    # Genera JSON
    if generate_gallery_json():
        print("✅ JSON generato")
    else:
        print("❌ Errore nella generazione JSON")
        return False
    
    # Genera HTML
    if generate_gallery_html():
        print("✅ HTML generato")
    else:
        print("❌ Errore nella generazione HTML")
        return False
    
    print("🎉 Galleria aggiornata con successo!")
    return True

if __name__ == "__main__":
    main()
