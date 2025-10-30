import os
import logging
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
from dotenv import load_dotenv

# Carica le variabili d'ambiente
load_dotenv()

# Configurazione logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Directory di destinazione per le immagini
IMAGE_DIR = '/var/www/romastudiotattoo/images'

# Assicurati che la directory esista
os.makedirs(IMAGE_DIR, exist_ok=True)

def update_gallery():
    """Aggiorna automaticamente la galleria dopo il caricamento di una nuova immagine"""
    try:
        # Esegui lo script di aggiornamento della galleria
        result = subprocess.run(
            ['python3', '/var/www/romastudiotattoo/update_gallery.py'],
            capture_output=True,
            text=True,
            cwd='/var/www/romastudiotattoo'
        )
        
        if result.returncode == 0:
            logging.info("Galleria aggiornata automaticamente")
            return True
        else:
            logging.error(f"Errore nell'aggiornamento della galleria: {result.stderr}")
            return False
            
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
    welcome_text = """
🤖 *Bot Galleria Foto Roma Studio Tattoo*

�� *Carica foto:* Invia semplicemente una foto o immagine
🗑️ *Comandi disponibili:*

/delete_last - Elimina l'ultima foto caricata
/delete_all - Elimina TUTTE le foto (⚠️ attenzione!)
/list - Mostra lista delle foto caricate
/help - Mostra questo messaggio

💡 *Nota:* Le foto eliminate vengono rimosse anche dalla galleria web automaticamente.
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra i comandi disponibili"""
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

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce le foto ricevute dal bot"""
    try:
        # Ottieni l'utente che ha inviato la foto
        user = update.effective_user
        username = user.username or user.first_name or str(user.id)

        # Ottieni la foto con la massima risoluzione
        photo = update.message.photo[-1]

        # Scarica la foto
        file = await context.bot.get_file(photo.file_id)
        file_path = os.path.join(IMAGE_DIR, f"{username}_{photo.file_id}.jpg")

        # Salva la foto
        await file.download_to_drive(file_path)

        # Aggiorna automaticamente la galleria
        gallery_updated = update_gallery()
        
        # Invia conferma
        if gallery_updated:
            await update.message.reply_text(f"✅ Foto caricata e galleria aggiornata!\n💾 Salvata come: `{os.path.basename(file_path)}`")
        else:
            await update.message.reply_text(f"Foto caricata ma errore nell'aggiornamento della galleria.\n💾 Salvata come: `{os.path.basename(file_path)}`")

        logging.info(f"Foto caricata da {username}: {file_path}")

    except Exception as e:
        logging.error(f"Errore nel caricamento della foto: {e}")
        await update.message.reply_text("❌ Errore nel caricamento della foto. Riprova.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce i documenti (immagini inviate come file)"""
    try:
        # Ottieni l'utente
        user = update.effective_user
        username = user.username or user.first_name or str(user.id)

        # Ottieni il documento
        document = update.message.document

        # Verifica che sia un'immagine
        if document.mime_type.startswith('image/'):
            file = await context.bot.get_file(document.file_id)
            file_path = os.path.join(IMAGE_DIR, f"{username}_{document.file_name or document.file_id}")

            # Salva il file
            await file.download_to_drive(file_path)

            # Aggiorna automaticamente la galleria
            gallery_updated = update_gallery()
            
            # Invia conferma
            if gallery_updated:
                await update.message.reply_text(f"✅ Immagine caricata e galleria aggiornata!\n💾 Salvata come: `{os.path.basename(file_path)}`")
            else:
                await update.message.reply_text(f"Immagine caricata ma errore nell'aggiornamento della galleria.\n💾 Salvata come: `{os.path.basename(file_path)}`")

            logging.info(f"Immagine caricata da {username}: {file_path}")
        else:
            await update.message.reply_text("📎 Invia solo immagini (foto o file immagine).")

    except Exception as e:
        logging.error(f"Errore nel caricamento del documento: {e}")
        await update.message.reply_text("❌ Errore nel caricamento dell'immagine. Riprova.")

def main():
    """Funzione principale"""
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

    # Aggiungi gli handler per foto e documenti
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))

    # Avvia il bot
    logging.info("🤖 Bot avviato con funzionalità di eliminazione. In attesa di messaggi...")
    application.run_polling()

if __name__ == '__main__':
    main()
