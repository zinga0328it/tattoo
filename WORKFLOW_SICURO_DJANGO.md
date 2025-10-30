# Workflow Sicuro per Sviluppo Siti Web con Django

## 🎯 Obiettivo
Questo documento descrive il workflow sicuro per sviluppare e deployare siti web con Django, evitando rischi di sicurezza e downtime del sito di produzione.

## 📁 Struttura delle Directory

```
/home/alex/web/tatuaggi/                    # Directory principale progetto
├── tattoo_gallery/                         # Progetto Django
│   ├── test_romastudiotattoo/             # 🧪 Directory di TEST/SVILUPPO
│   │   ├── index.html                     # File di sviluppo
│   │   ├── style.css                      # CSS di sviluppo
│   │   ├── gallery.js                     # JavaScript di sviluppo
│   │   └── ...                            # Altri file di sviluppo
│   └── tattoo_gallery/                    # Codice Django
│       ├── settings.py                    # ⚙️ Impostazioni Django
│       ├── urls.py                        # 🔗 URL routing
│       └── ...                            # Altri file Django
└── ...

/var/www/romastudiotattoo/                  # 🌐 Directory di PRODUZIONE
├── index.html                             # File live del sito
├── style.css                              # CSS live
├── gallery.js                             # JavaScript live
└── ...                                    # Altri file live
```

## 🔒 Workflow Sicuro - Regola d'Oro

**MAI modificare direttamente i file in produzione!**

### ✅ PASSO 1: Sviluppa nella Directory di Test
```bash
# Lavora sempre qui per modifiche e test
cd /home/alex/web/tatuaggi/tattoo_gallery/test_romastudiotattoo/
```

### ✅ PASSO 2: Testa le Modifiche Localmente
- Modifica i file nella directory `test_romastudiotattoo/`
- Testa le modifiche aprendo `file:///home/alex/web/tatuaggi/tattoo_gallery/test_romastudiotattoo/index.html` nel browser
- Verifica che tutto funzioni correttamente

### ✅ PASSO 3: Deploy in Produzione (Solo Dopo Test)
```bash
# Comando sicuro per deployare in produzione
sudo cp /home/alex/web/tatuaggi/tattoo_gallery/test_romastudiotattoo/index.html /var/www/romastudiotattoo/index.html
sudo cp /home/alex/web/tatuaggi/tattoo_gallery/test_romastudiotattoo/style.css /var/www/romastudiotattoo/style.css
sudo cp /home/alex/web/tatuaggi/tattoo_gallery/test_romastudiotattoo/gallery.js /var/www/romastudiotattoo/gallery.js
```

## 🚨 Pericoli da Evitare

### ❌ NON FARE MAI:
```bash
# PERICOLOSO: modifica diretta in produzione
nano /var/www/romastudiotattoo/index.html

# PERICOLOSO: deploy senza test
cp /home/alex/web/tatuaggi/tattoo_gallery/test_romastudiotattoo/index.html /var/www/romastudiotattoo/index.html  # senza sudo

# PERICOLOSO: modifiche simultanee
# Non modificare produzione mentre stai sviluppando
```

## 🔧 Comandi Essenziali

### Deploy Singolo File
```bash
sudo cp /home/alex/web/tatuaggi/tattoo_gallery/test_romastudiotattoo/index.html /var/www/romastudiotattoo/index.html
```

### Deploy Multipli File
```bash
sudo cp /home/alex/web/tatuaggi/tattoo_gallery/test_romastudiotattoo/*.html /var/www/romastudiotattoo/
sudo cp /home/alex/web/tatuaggi/tattoo_gallery/test_romastudiotattoo/*.css /var/www/romastudiotattoo/
sudo cp /home/alex/web/tatuaggi/tattoo_gallery/test_romastudiotattoo/*.js /var/www/romastudiotattoo/
```

### Verifica Deploy
```bash
# Controlla che i file siano stati copiati
ls -la /var/www/romastudiotattoo/
diff /home/alex/web/tatuaggi/tattoo_gallery/test_romastudiotattoo/index.html /var/www/romastudiotattoo/index.html
```

## 🛡️ Sicurezza Django

### ALLOWED_HOSTS
Nel file `tattoo_gallery/settings.py`:
```python
# ✅ SICURO: accetta solo domini autorizzati
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'romastudiotattoo.com',
    'www.romastudiotattoo.com',
    'romastudiotattoo.it',
    'www.romastudiotattoo.it'
]

# ❌ NON SICURO
# ALLOWED_HOSTS = ['*']  # Mai usare in produzione!
```

### DEBUG Mode
```python
# ✅ In produzione
DEBUG = False

# ❌ Mai in produzione
# DEBUG = True  # Espone informazioni sensibili
```

### SECRET_KEY
```python
# ✅ Usa chiave segreta sicura
SECRET_KEY = 'chiave-molto-lunga-e-complessa-generata-random'

# ❌ Non usare valori predefiniti
# SECRET_KEY = 'django-insecure-default-key'
```

## 🔄 Ciclo di Sviluppo Completo

1. **Modifica** → Directory `test_romastudiotattoo/`
2. **Test** → Browser locale o server di sviluppo
3. **Deploy** → Comando `sudo cp` in produzione
4. **Verifica** → Controlla sito live
5. **Backup** → Mantieni versioni funzionanti

## 📋 Checklist Pre-Deploy

- [ ] File testati nella directory di sviluppo
- [ ] Nessun errore JavaScript nella console
- [ ] Layout responsive verificato
- [ ] API endpoints funzionanti
- [ ] Backup del file precedente (opzionale)
- [ ] Permessi corretti sui file

## 🚑 Rollback in Caso di Problemi

```bash
# Se qualcosa va storto, ripristina dalla directory di test
sudo cp /home/alex/web/tatuaggi/tattoo_gallery/test_romastudiotattoo/index.html.backup /var/www/romastudiotattoo/index.html
```

## 📚 Best Practices

1. **Version Control**: Usa Git per tracciare le modifiche
2. **Backup Automatici**: Mantieni copie di backup dei file funzionanti
3. **Test Thorough**: Testa sempre prima del deploy
4. **Monitoraggio**: Controlla i log dopo il deploy
5. **Documentazione**: Aggiorna questo documento quando cambi workflow

## 🎯 Conclusione

Questo workflow garantisce:
- ✅ **Sicurezza**: Il sito di produzione non viene mai modificato direttamente
- ✅ **Stabilità**: Possibilità di rollback immediato
- ✅ **Test**: Tutto viene testato prima del deploy
- ✅ **Velocità**: Deploy rapidi con un semplice comando cp

**Ricorda**: La pazienza nel testare salva tempo nel fixare problemi in produzione!</content>
<parameter name="filePath">/home/alex/web/tatuaggi/WORKFLOW_SICURO_DJANGO.md
