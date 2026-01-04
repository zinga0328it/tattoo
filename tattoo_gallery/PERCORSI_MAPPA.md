# 📁 MAPPA DEI PERCORSI - Roma Studio Tattoo

## 🚨 IMPORTANTE: WORKFLOW DI LAVORO
1. **SVILUPPO**: Lavoriamo in `/home/alex/web/tatuaggi/tattoo_gallery/test_romastudiotattoo/`
2. **PRODUZIONE**: Alla fine copiamo tutto in `/var/www/romastudiotattoo/`
3. **TEST**: Testiamo con curl direttamente su `https://romastudiotattoo.com/`

---

## 📂 DIRECTORY STRUTTURA

### 🔧 DIRECTORY DI SVILUPPO (WORKSPACE)
```
/home/alex/web/tatuaggi/tattoo_gallery/test_romastudiotattoo/
├── index.html              # Homepage con galleria dinamica
├── gallery.html             # Galleria completa
├── detail.html              # Pagina dettaglio tatuaggio
├── gallery.js               # JavaScript originale
├── gallery-django.js        # JavaScript aggiornato per Django
├── style.css                # Stili CSS
├── favicon.ico              # Favicon
├── apple-touch-icon.png     # Icona Apple
├── robots.txt               # File robots
├── sitemap.xml              # Sitemap
├── gallery.json             # JSON generato
├── tattoos.json             # JSON alternativo
├── likes.json               # Sistema like
└── images/                  # Cartella immagini
    ├── *.jpg                # File immagini tatuaggi
    └── ...
```

### 🌐 DIRECTORY PUBBLICA (PRODUZIONE)
```
/var/www/romastudiotattoo/
├── index.html              # COPIA DA: test_romastudiotattoo/index.html
├── gallery.html             # COPIA DA: test_romastudiotattoo/gallery.html
├── detail.html              # COPIA DA: test_romastudiotattoo/detail.html
├── gallery-django.js        # COPIA DA: test_romastudiotattoo/gallery-django.js
├── style.css                # COPIA DA: test_romastudiotattoo/style.css
└── images/                  # Già presente (non toccare)
```

---

## 🔗 BACKEND DJANGO (SICURO)
```
/home/alex/web/tatuaggi/tattoo_gallery/
├── manage.py                # Django management
├── tattoo_gallery/
│   ├── settings.py          # Configurazione Django
│   └── urls.py              # URL routing
└── gallery/
    ├── models.py            # Modello Database
    ├── views.py             # API Views
    └── urls.py              # URL API
```

---

## 🔐 DATABASE
```
/home/alex/web/tatuaggi/tattoo_gallery.db
Tabella: tattoos
- id, telegram_id, username, description, filename, uploaded_at, file_id, likes
```

---

## 🌐 URL FINALI DI PRODUZIONE
- **Homepage**: `https://romastudiotattoo.com/`
- **Galleria**: `https://romastudiotattoo.com/gallery.html`
- **Dettaglio**: `https://romastudiotattoo.com/detail.html?id=X`
- **API**: `https://romastudiotattoo.com/gallery/api/tattoos/`

---

## 🚀 COMANDI PER DEPLOY
```bash
# 1. Copia file aggiornati nella directory pubblica
sudo cp /home/alex/web/tatuaggi/tattoo_gallery/test_romastudiotattoo/index.html /var/www/romastudiotattoo/
sudo cp /home/alex/web/tatuaggi/tattoo_gallery/test_romastudiotattoo/gallery.html /var/www/romastudiotattoo/
sudo cp /home/alex/web/tatuaggi/tattoo_gallery/test_romastudiotattoo/detail.html /var/www/romastudiotattoo/
sudo cp /home/alex/web/tatuaggi/tattoo_gallery/test_romastudiotattoo/gallery-django.js /var/www/romastudiotattoo/

# 2. Test con curl
curl -s https://romastudiotattoo.com/ | grep "galleria"
curl -s https://romastudiotattoo.com/gallery/api/tattoos/ | head -c 100

# 3. Verifica Django attivo
ps aux | grep "manage.py runserver"
```

---

## ⚠️ NOTE SICUREZZA
- ✅ Django gira SOLO su 127.0.0.1:8888 (interno)
- ✅ File Python in `/home/alex/web/tatuaggi/` (SICURO)
- ✅ File HTML in `/var/www/romastudiotattoo/` (PUBBLICO)
- ✅ Apache proxy per `/gallery/` → Django interno

---

## 🎯 TODO CHECKLIST
- [x] ✅ index.html - percorsi API corretti (/gallery/api/tattoos/)
- [x] ✅ gallery.html - percorsi API corretti (/gallery/api/tattoos/) 
- [x] ✅ detail.html - percorsi API corretti (/gallery/api/tattoo/, /gallery/api/artist/)
- [ ] 🚀 Deploy in produzione
- [ ] 🧪 Test finale con curl su URL reali

## ✅ STATO CORRENTE
Tutti i file HTML hanno i percorsi API corretti:
- `/gallery/api/tattoos/` - API generale tatuaggi
- `/gallery/api/tattoo/{id}/` - API dettaglio singolo tatuaggio  
- `/gallery/api/artist/{username}/` - API tatuaggi per artista

PRONTI PER IL DEPLOY! 🚀
