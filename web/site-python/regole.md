# Regole Operative per Site-Python.com

## Struttura delle Cartelle
- **Cartella Pubblica**: `/var/www/site-python` - Contiene solo file HTML pubblicati. Accessibile dal web.
- **Cartella Privata**: `/home/alex/web/site-python` - Contiene file Python (.py), script e logica del sito. Non accessibile pubblicamente.
- **Sottocartella Sviluppo**: `/home/alex/web/site-python/web` - Per file HTML temporanei/di sviluppo. Copiare da qui alla cartella pubblica per pubblicare.

## Configurazione Server
- **Apache Virtual Host**: Configurato per HTTP e HTTPS su `site-python.com` e `www.site-python.com`.
- **HTTPS con Let's Encrypt**: Certificato automatico, rinnovo programmato.
- **DNS su Cloudflare**: Record A per @ e CNAME per www, puntanti all'IP pubblico del server (93.57.240.131).

## Rete Yggdrasil
- **Scopo**: Rete decentralizzata per connessioni sicure e isolate, usata per database e comunicazioni interne.
- **Chiave Pubblica PC Locale**: `7f60feae68823fa25a830dbda5f2e3b05d80be7dd40e84667b47a6ef9023eee7`
- **Chiave Pubblica Server DB**: `def0ce3d5aba11ac798273400b1e45002a90b660b3bfda2104c74609fbcb8203`
- **Configurazione**: Peer principale `tls://93.57.240.131:55555`, `AllowedPublicKeys` limitate al server DB, `NodeInfo` "Alex-PC".
- **Test**: Peer connesso con RTT ~2.66ms, traffico attivo.

## File e API Remoti
- **Server API Remoto**: API Flask ospitata su un PC separato nella rete Yggdrasil (IP Ygg: `[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]`, porta 7123).
- **File Remoti**:
  - `~/yggdrasil/database/api.py`: App Flask con endpoint per dipendenti, utenti, login, ecc.
  - `~/yggdrasil/database/dipendenti.py`: Classi Dipendente e DipendenteA per gestione stipendi e malattia.
  - `~/yggdrasil/database/database.py`: Classe YggdrasilDatabase per gestione DB SQLite con utenti, pagamenti, progressi.
- **Sicurezza API**: Richiede header `X-API-Key: 16e91aab57262cbc01e89abfb5bfc519496197ea51ee31a00ebf957ff30cff47`, accessibile solo dalla rete Yggdrasil (verifica IPv6 Ygg).
- **Comunicazione**: Tutte le chiamate API tra PC locali e remoti avvengono via Yggdrasil per isolamento e sicurezza. Usare `scp` o `rsync` per trasferire file tra PC via Ygg IP.
- **Endpoint Principali**:
  - `/api/dipendenti`: GET (lista), POST (aggiungi).
  - `/api/dipendenti/<matricola>`: GET (singolo).
  - `/api/dipendenti/<matricola>/paga`: POST (calcola stipendio).
  - `/api/dipendenti/<matricola>/malattia`: POST (aggiungi giorni malattia).
  - Altri per utenti, login, progressi.

## Sicurezza e Best Practices
- **Ambiente Virtuale Python**: Usare sempre virtualenv per isolare dipendenze e codice Python.
- **Porte Interne e Proxy Interni**: Utilizzare sempre porte interne con proxy interni per la comunicazione sicura.
- **Database**: Database solo su Yggdrasil, ospitato su un altro PC della stessa rete (IP 93.57.240.131), accessibile via rete Yggdrasil per massima sicurezza e isolamento.

## Operazioni
- Pubblicare: Copiare file HTML da `web` a `/var/www/site-python` dopo test.
- Non esporre mai file .py pubblicamente.
- Ricaricare Apache dopo modifiche ai conf: `sudo systemctl reload apache2`.
- Monitorare log per sicurezza.
- Riavviare Yggdrasil dopo modifiche config: `sudo systemctl restart yggdrasil`.
- **Aggiornare File Remoti**: Usare `scp` per copiare file da locale a remoto via Ygg IP, es. `scp dipendenti.py user@[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:~/yggdrasil/database/`.
- **Test API**: Usare `curl` con header API key, es. `curl -H "X-API-Key: 16e91aab57262cbc01e89abfb5bfc519496197ea51ee31a00ebf957ff30cff47" http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:7123/api/dipendenti`.
- **Backup**: Salvare versioni dei file remoti prima di modifiche.

**Stato Progetto**: Completato con successo! Sistema isolato su Yggdrasil, demo funzionante su site-python.com/dipendenti.html, brevetto documentato.

Queste regole assicurano un setup professionale, sicuro e scalabile.
