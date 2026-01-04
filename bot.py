import os
import logging
import subprocess
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, CallbackQueryHandler, filters
from dotenv import load_dotenv

# Configurazione del logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('/home/alex/web/tatuaggi/bot.log'),
        logging.StreamHandler()
    ]
)

# Carica le variabili d'ambiente
load_dotenv()
# ID degli amministratori che devono approvare le foto (separati da virgola)
admin_ids_str = os.getenv("ADMIN_TELEGRAM_IDS")
if not admin_ids_str:
    logging.error("❌ ADMIN_TELEGRAM_IDS non trovato nel file .env")
    exit(1)
ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(",")]


# Directory di destinazione per le immagini
IMAGE_DIR = '/var/www/romastudiotattoo/images'

# Database per salvare le informazioni dei tatuaggi
DB_FILE = "/home/alex/web/tatuaggi/tattoo_gallery.db"

# Dizionario per tracciare gli utenti che stanno fornendo descrizioni
pending_descriptions = {}

# Assicurati che la directory esista
os.makedirs(IMAGE_DIR, exist_ok=True)

def cleanup_temp_files():
    """Pulisce i file temporanei più vecchi di 24 ore"""
    try:
        import time
        current_time = time.time()
        cleanup_count = 0
        
        if not os.path.exists(IMAGE_DIR):
            return cleanup_count
        
        for filename in os.listdir(IMAGE_DIR):
            if filename.startswith('temp_'):
                file_path = os.path.join(IMAGE_DIR, filename)
                try:
                    # Se il file è più vecchio di 24 ore (86400 secondi)
                    if current_time - os.path.getmtime(file_path) > 86400:
                        os.remove(file_path)
                        cleanup_count += 1
                        logging.info(f"File temporaneo rimosso: {filename}")
                except Exception as e:
                    logging.error(f"Errore nella rimozione del file temporaneo {filename}: {e}")
        
        if cleanup_count > 0:
            logging.info(f"Cleanup completato: {cleanup_count} file temporanei rimossi")
        
        return cleanup_count
    except Exception as e:
        logging.error(f"Errore nel cleanup dei file temporanei: {e}")
        return 0

def init_database():
    """Inizializza il database e crea le tabelle se non esistono"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Crea tabella per i tatuaggi
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tattoos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            username TEXT,
            description TEXT NOT NULL,
            filename TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_id TEXT
        )
    ''')
    
    # Crea tabella per le foto in attesa di approvazione
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pending_approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            username TEXT,
            description TEXT NOT NULL,
            temp_filename TEXT NOT NULL,
            file_id TEXT NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message_id INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()
    logging.info("Database inizializzato")

def save_tattoo(telegram_id, username, description, filename, file_id):
    """Salva le informazioni di un tatuaggio nel database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tattoos (telegram_id, username, description, filename, file_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (telegram_id, username, description, filename, file_id))
        
        conn.commit()
        conn.close()
        logging.info(f"Tatuaggio salvato nel database: {filename}")
        return True
    except Exception as e:
        logging.error(f"Errore nel salvataggio nel database: {e}")
        return False

def get_user_tattoos(telegram_id):
    """Ottiene tutti i tatuaggi caricati da un utente"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, description, filename, uploaded_at
            FROM tattoos
            WHERE telegram_id = ?
            ORDER BY uploaded_at DESC
        ''', (telegram_id,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        logging.error(f"Errore nel recupero tatuaggi utente: {e}")
        return []

def delete_tattoo_from_db(filename):
    """Rimuove un tatuaggio dal database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM tattoos WHERE filename = ?', (filename,))
        
        conn.commit()
        conn.close()
        logging.info(f"Tatuaggio rimosso dal database: {filename}")
        return True
    except Exception as e:
        logging.error(f"Errore nella rimozione dal database: {e}")
        return False

def save_pending_approval(telegram_id, username, description, temp_filename, file_id):
    """Salva una foto in attesa di approvazione"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pending_approvals (telegram_id, username, description, temp_filename, file_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (telegram_id, username, description, temp_filename, file_id))
        
        approval_id = cursor.lastrowid
        conn.commit()
        conn.close()
        logging.info(f"Foto in attesa di approvazione salvata: {temp_filename}")
        return approval_id
    except Exception as e:
        logging.error(f"Errore nel salvataggio pending approval: {e}")
        return None

def approve_tattoo(approval_id):
    """Approva una foto e la sposta nella galleria"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Ottieni i dati della foto in attesa
        cursor.execute("SELECT * FROM pending_approvals WHERE id = ?", (approval_id,))
        approval = cursor.fetchone()
        
        if not approval:
            return False, None
        
        telegram_id, username, description, temp_filename, file_id, submitted_at, message_id = approval[1:8]
        
        # Crea il nome file finale
        safe_description = "".join(c for c in description if c.isalnum() or c in " _-").strip()[:50]
        final_filename = f"{username}_{safe_description}_{file_id}.jpg"
        final_path = os.path.join(IMAGE_DIR, final_filename)
        temp_path = os.path.join(IMAGE_DIR, temp_filename)
        
        # Sposta il file
        os.rename(temp_path, final_path)
        
        # Salva nel database principale
        save_tattoo(telegram_id, username, description, final_filename, file_id)
        
        # Rimuovi dalla tabella pending
        cursor.execute("DELETE FROM pending_approvals WHERE id = ?", (approval_id,))
        
        conn.commit()
        conn.close()
        
        # Aggiorna galleria
        update_gallery()
        
        logging.info(f"Foto approvata e pubblicata: {final_filename}")
        return True, telegram_id
    except Exception as e:
        logging.error(f"Errore nell'approvazione: {e}")
        return False, None

def reject_tattoo(approval_id):
    """Rifiuta una foto e la elimina"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Ottieni il nome del file temporaneo e l'ID utente
        cursor.execute("SELECT temp_filename, telegram_id FROM pending_approvals WHERE id = ?", (approval_id,))
        result = cursor.fetchone()
        
        user_id = None
        if result:
            temp_filename, user_id = result
            temp_path = os.path.join(IMAGE_DIR, temp_filename)
            
            # Elimina il file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        # Rimuovi dalla tabella pending
        cursor.execute("DELETE FROM pending_approvals WHERE id = ?", (approval_id,))
        
        conn.commit()
        conn.close()
        
        logging.info(f"Foto rifiutata: {temp_filename}")
        return True, user_id
    except Exception as e:
        logging.error(f"Errore nel rifiuto: {e}")
        return False, None

def update_gallery():
    """Aggiorna automaticamente la galleria dopo il caricamento di una nuova immagine"""
    try:
        # Esegui lo script di aggiornamento della galleria (PERCORSO SICURO!)
        result = subprocess.run(
            ['python3', '/home/alex/web/tatuaggi/update_gallery.py'],
            capture_output=True,
            text=True,
            cwd='/home/alex/web/tatuaggi'
        )
        
        gallery_success = result.returncode == 0
        if gallery_success:
            logging.info("Galleria aggiornata automaticamente")
        else:
            logging.error(f"Errore nell'aggiornamento della galleria: {result.stderr}")
        
        # Aggiorna anche i dati della homepage
        homepage_result = subprocess.run(
            ['python3', '/home/alex/web/tatuaggi/update_homepage_data.py'],
            capture_output=True,
            text=True,
            cwd='/home/alex/web/tatuaggi'
        )
        
        homepage_success = homepage_result.returncode == 0
        if homepage_success:
            logging.info("Homepage aggiornata automaticamente")
        else:
            logging.error(f"Errore nell'aggiornamento della homepage: {homepage_result.stderr}")
        
        return gallery_success and homepage_success
            
    except Exception as e:
        logging.error(f"Errore nell'esecuzione dello script di aggiornamento: {e}")
        return False

def get_image_list():
    """Ottiene la lista delle immagini ordinate per data di modifica (più recenti prima)"""
    if not os.path.exists(IMAGE_DIR):
        return []
    
    images = []
    for file in os.listdir(IMAGE_DIR):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            file_path = os.path.join(IMAGE_DIR, file)
            mtime = os.path.getmtime(file_path)
            images.append((file, mtime))
    
    # Ordina per data di modifica (più recenti prima)
    images.sort(key=lambda x: x[1], reverse=True)
    return [img[0] for img in images]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Messaggio di benvenuto con comandi disponibili"""
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name or str(user.id)
    
    # Verifica se è un amministratore
    is_admin = user_id in ADMIN_IDS
    
    welcome_text = f"""
🤖 **Bot Galleria Foto Roma Studio Tattoo**

� Ciao {username}! {"🔧 *[AMMINISTRATORE]*" if is_admin else ""}

📸 **COME CARICARE UNA FOTO:**
1️⃣ Invia una foto del tatuaggio
2️⃣ Scrivi una descrizione quando richiesta
3️⃣ Aspetta l'approvazione dell'admin
4️⃣ Riceverai una notifica quando sarà pubblicata!

🎯 **COMANDI DISPONIBILI:**

👤 **Comandi Utente:**
📤 Invia foto → Carica un tatuaggio con descrizione
/my_tattoos → Mostra i tuoi tatuaggi caricati
/help → Mostra questo menu

🔧 **Comandi Amministratore:**{f'''
/pending → Mostra foto in attesa di approvazione
/stats → Statistiche complete del bot
/update_gallery → Forza aggiornamento galleria
/list → Lista di tutte le foto caricate
/delete_last → Elimina l'ultima foto caricata
/delete_all → Elimina TUTTE le foto (⚠️ ATTENZIONE!)''' if is_admin else '''
ℹ️ Solo per amministratori'''}

📋 **FORMATI SUPPORTATI:**
• Foto: JPG, PNG, GIF, WebP
• Documenti: Immagini inviate come file

💡 **NOTE IMPORTANTI:**
• Tutte le foto richiedono approvazione admin
• Le foto eliminate vengono rimosse automaticamente dalla galleria web
• Riceverai notifiche sullo stato delle tue foto
• Descrivi chiaramente il tatuaggio per facilitare l'approvazione

🌐 **Galleria Web:** Le foto approvate appariranno automaticamente sul sito!
"""
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra i comandi disponibili - chiama start per coerenza"""
    await start(update, context)

async def delete_last(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Elimina l'ultima immagine caricata"""
    try:
        images = get_image_list()
        if not images:
            await update.message.reply_text("❌ Nessuna immagine da eliminare.")
            return
        
        last_image = images[0]
        image_path = os.path.join(IMAGE_DIR, last_image)
        
        # Rimuovi anche dal database
        db_deleted = delete_tattoo_from_db(last_image)
        if not db_deleted:
            logging.warning(f"Errore nella rimozione dal database per {last_image}")
        
        # Elimina il file
        os.remove(image_path)
        
        # Aggiorna la galleria
        gallery_updated = update_gallery()
        
        if gallery_updated:
            await update.message.reply_text(f"✅ Ultima immagine eliminata: `{last_image}`\nGalleria aggiornata automaticamente.")
        else:
            await update.message.reply_text(f"✅ Immagine eliminata: `{last_image}`\n⚠️ Errore nell'aggiornamento della galleria.")
        
        logging.info(f"Immagine eliminata: {last_image}")
        
    except Exception as e:
        logging.error(f"Errore nell'eliminazione dell'immagine: {e}")
        await update.message.reply_text("❌ Errore nell'eliminazione dell'immagine.")

async def delete_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Elimina tutte le immagini (con conferma)"""
    try:
        images = get_image_list()
        if not images:
            await update.message.reply_text("❌ Nessuna immagine da eliminare.")
            return
        
        # Chiedi conferma
        keyboard = [
            [{"text": "✅ SÌ, elimina tutto", "callback_data": "confirm_delete_all"}],
            [{"text": "❌ NO, annulla", "callback_data": "cancel_delete_all"}]
        ]
        
        await update.message.reply_text(
            f"⚠️ *ATTENZIONE!* Vuoi eliminare {len(images)} immagini?\n\nQuesta azione è irreversibile!",
            parse_mode='Markdown',
            reply_markup={"inline_keyboard": keyboard}
        )
        
    except Exception as e:
        logging.error(f"Errore nel comando delete_all: {e}")
        await update.message.reply_text("❌ Errore nel processamento del comando.")

async def list_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra la lista delle immagini caricate"""
    try:
        images = get_image_list()
        if not images:
            await update.message.reply_text("📭 Nessuna immagine caricata.")
            return
        
        message = "🖼️ *Immagini caricate:*\n\n"
        for i, img in enumerate(images[:10], 1):  # Mostra max 10 immagini
            message += f"{i}. `{img}`\n"
        
        if len(images) > 10:
            message += f"\n... e altre {len(images) - 10} immagini"
        
        message += f"\n\n📊 *Totale:* {len(images)} immagini"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logging.error(f"Errore nel comando list: {e}")
        await update.message.reply_text("❌ Errore nel recupero della lista immagini.")

async def my_tattoos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra i tatuaggi caricati dall'utente corrente"""
    try:
        user = update.effective_user
        user_id = user.id
        
        tattoos = get_user_tattoos(user_id)
        
        if not tattoos:
            await update.message.reply_text("📭 Non hai ancora caricato nessun tatuaggio.")
            return
        
        message = f"🖼️ *I tuoi tatuaggi caricati:*\n\n"
        for tattoo in tattoos[:10]:  # Mostra max 10
            tattoo_id, description, filename, uploaded_at = tattoo
            message += f"🆔 `{tattoo_id}` - 📝 {description}\n"
            message += f"📅 {uploaded_at}\n\n"
        
        if len(tattoos) > 10:
            message += f"... e altri {len(tattoos) - 10} tatuaggi"
        
        message += f"\n\n📊 *Totale:* {len(tattoos)} tatuaggi"
        
        await update.message.reply_text(message, parse_mode="Markdown")
        
    except Exception as e:
        logging.error(f"Errore nel comando my_tattoos: {e}")
        await update.message.reply_text("❌ Errore nel recupero dei tuoi tatuaggi.")

async def pending_approvals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra le foto in attesa di approvazione (solo admin)"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Comando riservato all'amministratore.")
        return
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM pending_approvals")
        count = cursor.fetchone()[0]
        
        if count == 0:
            await update.message.reply_text("📭 Nessuna foto in attesa di approvazione.")
            return
        
        cursor.execute("""
            SELECT id, telegram_id, username, description, submitted_at
            FROM pending_approvals 
            ORDER BY submitted_at DESC
        """)
        
        approvals = cursor.fetchall()
        conn.close()
        
        message = f"⏳ *Foto in attesa di approvazione: {count}*\n\n"
        
        for approval in approvals[:10]:  # Mostra max 10
            approval_id, telegram_id, username, description, submitted_at = approval
            message += f"🆔 `{approval_id}` - 👤 {username} (ID: `{telegram_id}`)\n"
            message += f"📝 {description}\n"
            message += f"📅 {submitted_at}\n\n"
        
        if len(approvals) > 10:
            message += f"... e altre {len(approvals) - 10} foto"
        
        await update.message.reply_text(message, parse_mode="Markdown")
        
    except Exception as e:
        logging.error(f"Errore in pending_approvals: {e}")
        await update.message.reply_text("❌ Errore nel recupero delle approvazioni.")

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra statistiche complete (solo admin)"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Comando riservato all'amministratore.")
        return
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Conta foto approvate
        cursor.execute("SELECT COUNT(*) FROM tattoos")
        approved_count = cursor.fetchone()[0]
        
        # Conta foto in attesa
        cursor.execute("SELECT COUNT(*) FROM pending_approvals")
        pending_count = cursor.fetchone()[0]
        
        # Utenti attivi (che hanno caricato almeno una foto)
        cursor.execute("SELECT COUNT(DISTINCT telegram_id) FROM tattoos")
        active_users = cursor.fetchone()[0]
        
        # Utenti in attesa
        cursor.execute("SELECT COUNT(DISTINCT telegram_id) FROM pending_approvals")
        pending_users = cursor.fetchone()[0]
        
        # Ultima foto caricata
        cursor.execute("SELECT uploaded_at FROM tattoos ORDER BY uploaded_at DESC LIMIT 1")
        last_upload = cursor.fetchone()
        last_upload_str = last_upload[0] if last_upload else "Nessuna"
        
        conn.close()
        
        # Conta file fisici
        physical_files = len(get_image_list())
        
        stats_message = f"""
📊 **STATISTICHE BOT GALLERIA**

🖼️ **FOTO:**
✅ Foto approvate: `{approved_count}`
⏳ In attesa di approvazione: `{pending_count}`
📁 File fisici nella galleria: `{physical_files}`

👥 **UTENTI:**
👤 Utenti attivi: `{active_users}`
⌛ Utenti con foto in attesa: `{pending_users}`

📅 **ATTIVITÀ:**
🕒 Ultima foto caricata: `{last_upload_str}`

🔧 **AMMINISTRATORI:**
"""
        
        for i, admin_id in enumerate(ADMIN_IDS, 1):
            stats_message += f"`{i}.` ID: `{admin_id}`\n"
        
        await update.message.reply_text(stats_message, parse_mode="Markdown")
        
    except Exception as e:
        logging.error(f"Errore in admin_stats: {e}")
        await update.message.reply_text("❌ Errore nel recupero delle statistiche.")

async def force_update_gallery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forza aggiornamento manuale della galleria (solo admin)"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Comando riservato all'amministratore.")
        return
    
    await update.message.reply_text("🔄 Aggiornamento galleria in corso...")
    
    try:
        # Aggiorna galleria
        gallery_updated = update_gallery()
        
        if gallery_updated:
            await update.message.reply_text("✅ Galleria aggiornata con successo!")
        else:
            await update.message.reply_text("❌ Errore nell'aggiornamento galleria")
        
        logging.info(f"Aggiornamento manuale galleria richiesto da admin {user_id}")
        
    except Exception as e:
        logging.error(f"Errore in force_update_gallery: {e}")
        await update.message.reply_text("❌ Errore durante l'aggiornamento manuale.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce le foto ricevute dal bot - ora chiede descrizione"""
    try:
        # Ottieni l'utente che ha inviato la foto
        user = update.effective_user
        user_id = user.id
        username = user.username or user.first_name or str(user.id)

        # Controlla se l'utente ha già una foto in attesa di descrizione
        if user_id in pending_descriptions:
            await update.message.reply_text(
                "⚠️ Hai già una foto in attesa di descrizione!\n\n"
                "Per favore, fornisci prima la descrizione della foto precedente."
            )
            return

        # Controlla se l'utente ha troppe foto in attesa di approvazione
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM pending_approvals WHERE telegram_id = ?", (user_id,))
            pending_count = cursor.fetchone()[0]
            conn.close()
            
            if pending_count >= 3:  # Limite di 3 foto in attesa per utente
                await update.message.reply_text(
                    "⚠️ Hai già 3 foto in attesa di approvazione!\n\n"
                    "Attendi che vengano elaborate prima di inviarne altre."
                )
                return
        except Exception as e:
            logging.error(f"Errore nel controllo pending: {e}")

        # Ottieni la foto con la massima risoluzione
        photo = update.message.photo[-1]

        # Crea un nome file temporaneo
        temp_filename = f"temp_{user_id}_{photo.file_id}.jpg"
        temp_file_path = os.path.join(IMAGE_DIR, temp_filename)

        # Scarica la foto temporaneamente
        file = await context.bot.get_file(photo.file_id)
        await file.download_to_drive(temp_file_path)

        # Registra l'utente come in attesa di descrizione
        pending_descriptions[user_id] = {
            "temp_file": temp_file_path,
            "username": username,
            "file_id": photo.file_id
        }

        # Chiedi la descrizione
        await update.message.reply_text(
            "📝 *Perfetto!* Ora dimmi una breve descrizione di questo tatuaggio.\n\n" 
            "📋 *Esempi:* \"Rosa con spine sul braccio\" o \"Drago tradizionale sulla schiena\"\n\n" 
            "✍️ Scrivi la descrizione qui sotto 👇\n\n"
            "💡 *Suggerimento:* Più dettagliata è la descrizione, più facile sarà l'approvazione!",
            parse_mode="Markdown"
        )

        logging.info(f"Foto ricevuta da {username} (ID: {user_id}), in attesa di descrizione")

    except Exception as e:
        logging.error(f"Errore nel caricamento della foto: {e}")
        await update.message.reply_text("❌ Errore nel caricamento della foto. Riprova.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce i documenti (immagini inviate come file) - ora chiede descrizione"""
    try:
        # Ottieni l'utente
        user = update.effective_user
        user_id = user.id
        username = user.username or user.first_name or str(user.id)

        # Ottieni il documento
        document = update.message.document

        # Verifica che sia un'immagine
        if document.mime_type.startswith('image/'):
            # Crea un nome file temporaneo
            temp_filename = f"temp_{user_id}_{document.file_id}"
            temp_file_path = os.path.join(IMAGE_DIR, temp_filename)

            # Scarica il file temporaneamente
            file = await context.bot.get_file(document.file_id)
            await file.download_to_drive(temp_file_path)

            # Registra l'utente come in attesa di descrizione
            pending_descriptions[user_id] = {
                "temp_file": temp_file_path,
                "username": username,
                "file_id": document.file_id,
                "original_name": document.file_name
            }

            # Chiedi la descrizione
            await update.message.reply_text(
                "📝 *Perfetto!* Ora dimmi una breve descrizione di questo tatuaggio.\n\n" 
                "Ad esempio: \"Rosa con spine sul braccio\" o \"Drago tradizionale sulla schiena\".\n\n" 
                "Scrivi la descrizione qui sotto 👇",
                parse_mode="Markdown"
            )

            logging.info(f"Documento immagine ricevuto da {username}, in attesa di descrizione")
        else:
            await update.message.reply_text("📎 Invia solo immagini (foto o file immagine).")

    except Exception as e:
        logging.error(f"Errore nel caricamento del documento: {e}")
        await update.message.reply_text("❌ Errore nel caricamento dell'immagine. Riprova.")

async def send_approval_request(context, approval_id, username, description, temp_filename):
    """Invia richiesta di approvazione all'amministratore"""
    try:
        # Invia la foto all'amministratore
        with open(os.path.join(IMAGE_DIR, temp_filename), 'rb') as photo_file:
            message = await context.bot.send_photo(
                chat_id=ADMIN_IDS[0],
                photo=photo_file,
                caption=f"🖼️ *Nuova foto da approvare*\n\n👤 *Utente:* {username}\n📝 *Descrizione:* {description}\n\nApprovi questa foto?",
                parse_mode="Markdown",
                reply_markup={
                    "inline_keyboard": [
                        [{"text": "✅ Approva", "callback_data": f"approve_{approval_id}"}],
                        [{"text": "❌ Rifiuta", "callback_data": f"reject_{approval_id}"}]
                    ]
                }
            )
        
        # Salva l'ID del messaggio per poterlo aggiornare dopo
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE pending_approvals SET message_id = ? WHERE id = ?", (message.message_id, approval_id))
        conn.commit()
        conn.close()
        
        logging.info(f"Richiesta di approvazione inviata per foto {temp_filename}")
        return True
    except Exception as e:
        logging.error(f"Errore nell'invio richiesta approvazione: {e}")
        return False

async def handle_text_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce le descrizioni fornite dagli utenti"""
    try:
        user = update.effective_user
        user_id = user.id
        text = update.message.text.strip()

        # Controlla se l'utente sta fornendo una descrizione
        if user_id in pending_descriptions:
            user_data = pending_descriptions[user_id]
            temp_file_path = user_data["temp_file"]
            username = user_data["username"]
            file_id = user_data["file_id"]

            # Salva in pending approvals invece di pubblicare direttamente
            approval_id = save_pending_approval(user_id, username, text, os.path.basename(temp_file_path), file_id)
            
            if approval_id:
                # Invia richiesta di approvazione all'amministratore
                approval_sent = await send_approval_request(context, approval_id, username, text, os.path.basename(temp_file_path))
                
                if approval_sent:
                    await update.message.reply_text(
                        f"✅ *Foto ricevuta!*\n\n" 
                        f"📝 *Descrizione:* {text}\n\n" 
                        f"⏳ La tua foto è stata inviata per l'approvazione. Riceverai una notifica quando sarà pubblicata!",
                        parse_mode="Markdown"
                    )
                    # Rimuovi dall'elenco delle descrizioni in attesa
                    del pending_descriptions[user_id]
                    
                    logging.info(f"Foto in attesa di approvazione da {username}: {os.path.basename(temp_file_path)}")
                else:
                    await update.message.reply_text("❌ Errore nell'invio per approvazione. Riprova.")
            else:
                await update.message.reply_text("❌ Errore nel salvataggio temporaneo. Riprova.")

    except Exception as e:
        logging.error(f"Errore nella gestione della descrizione: {e}")
        await update.message.reply_text("❌ Errore nel salvataggio della descrizione. Riprova.")

async def handle_approval_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce le callback di approvazione/rifiuto"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    # Gestisci callback per delete_all
    if callback_data == "confirm_delete_all":
        await handle_confirm_delete_all(query, context)
        return
    elif callback_data == "cancel_delete_all":
        await query.edit_message_text("❌ Operazione annullata. Nessuna immagine è stata eliminata.")
        return
    
    # Gestisci callback per approvazioni
    action, approval_id = callback_data.split("_")
    approval_id = int(approval_id)
    
    if action == "approve":
        success, user_id = approve_tattoo(approval_id)
        if success:
            await query.edit_message_caption(
                caption=query.message.caption + "\n\n✅ *APPROVATA e pubblicata!*",
                parse_mode="Markdown"
            )
            # Notifica l'utente
            if user_id:
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="🎉 *Fantastico!* La tua foto è stata approvata e pubblicata nella galleria!\n\nGrazie per aver condiviso il tuo tatuaggio!",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logging.error(f"Errore nell'invio notifica approvazione a {user_id}: {e}")
        else:
            await query.edit_message_caption(
                caption=query.message.caption + "\n\n❌ *Errore nell'approvazione*",
                parse_mode="Markdown"
            )
    
    elif action == "reject":
        success, user_id = reject_tattoo(approval_id)
        if success:
            await query.edit_message_caption(
                caption=query.message.caption + "\n\n❌ *RIFIUTATA*",
                parse_mode="Markdown"
            )
            # Notifica l'utente
            if user_id:
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="😔 La tua foto non è stata approvata per la pubblicazione.\n\nPuoi riprovare con un'altra immagine seguendo le linee guida.",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logging.error(f"Errore nell'invio notifica rifiuto a {user_id}: {e}")
        else:
            await query.edit_message_caption(
                caption=query.message.caption + "\n\n❌ *Errore nel rifiuto*",
                parse_mode="Markdown"
            )

async def handle_confirm_delete_all(query, context):
    """Gestisce la conferma per eliminare tutte le immagini"""
    try:
        images = get_image_list()
        deleted_count = 0
        
        for image in images:
            image_path = os.path.join(IMAGE_DIR, image)
            try:
                # Rimuovi dal database
                delete_tattoo_from_db(image)
                # Elimina il file
                os.remove(image_path)
                deleted_count += 1
            except Exception as e:
                logging.error(f"Errore nell'eliminazione di {image}: {e}")
        
        # Aggiorna la galleria
        gallery_updated = update_gallery()
        
        if gallery_updated:
            await query.edit_message_text(
                f"✅ Eliminate {deleted_count} immagini.\nGalleria aggiornata automaticamente."
            )
        else:
            await query.edit_message_text(
                f"✅ Eliminate {deleted_count} immagini.\n⚠️ Errore nell'aggiornamento della galleria."
            )
        
        logging.info(f"Eliminate {deleted_count} immagini totali")
        
    except Exception as e:
        logging.error(f"Errore nell'eliminazione di tutte le immagini: {e}")
        await query.edit_message_text("❌ Errore nell'eliminazione delle immagini.")

def main():
    """Funzione principale"""
    # Inizializza il database
    init_database()
    
    # Pulisci file temporanei vecchi
    cleanup_count = cleanup_temp_files()
    if cleanup_count > 0:
        logging.info(f"🧹 Cleanup iniziale: {cleanup_count} file temporanei rimossi")
    
    # Ottieni il token dal file .env
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logging.error("❌ Token del bot non trovato nel file .env")
        return

    # Crea l'applicazione
    application = ApplicationBuilder().token(token).build()

    # Aggiungi gli handler per i comandi
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("delete_last", delete_last))
    application.add_handler(CommandHandler("delete_all", delete_all))
    application.add_handler(CommandHandler("list", list_images))
    application.add_handler(CommandHandler("my_tattoos", my_tattoos))
    application.add_handler(CommandHandler("pending", pending_approvals))
    application.add_handler(CommandHandler("stats", admin_stats))
    application.add_handler(CommandHandler("update_gallery", force_update_gallery))

    # Aggiungi gli handler per foto e documenti
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))

    # Aggiungi l'handler per le descrizioni (messaggi di testo)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_description))

    # Aggiungi l'handler per le callback di approvazione
    application.add_handler(CallbackQueryHandler(handle_approval_callback))

    # Avvia il bot
    logging.info("🤖 Bot avviato con sistema di approvazione. In attesa di messaggi...")
    application.run_polling()

if __name__ == '__main__':
    main()
