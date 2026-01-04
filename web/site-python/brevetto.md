# Richiesta di Brevetto: Sistema di Isolamento e Sicurezza per Applicazioni Web Distribuite

## Titolo dell'Invenzione
Sistema e Metodo per l'Isolamento Sicuro di Database e API in Reti Decentralizzate utilizzando Yggdrasil per Applicazioni Web Distribuite

## Campo Tecnico
Il presente brevetto riguarda sistemi informatici, reti di comunicazione decentralizzate, sicurezza informatica e architetture web distribuite, in particolare l'isolamento di database e API da reti pubbliche utilizzando la rete Yggdrasil.

## Stato dell'Arte
Attualmente, le applicazioni web utilizzano database e API accessibili tramite internet pubblico, esponendoli a rischi di sicurezza come attacchi DDoS, SQL injection e accessi non autorizzati. Soluzioni esistenti includono VPN (es. OpenVPN), firewall tradizionali e crittografia TLS, ma queste non forniscono isolamento completo in reti decentralizzate e richiedono configurazione centralizzata. Tor

## Problema Risolto
Il problema principale è l'esposizione di database e API a internet pubblico, che compromette la sicurezza e la privacy. È necessario un sistema che isoli completamente il backend (database e API) in una rete privata decentralizzata, permettendo al frontend pubblico di interagire in modo sicuro senza esporre indirizzi privati.

## Descrizione dell'Invenzione
L'invenzione consiste in un sistema distribuito che utilizza la rete Yggdrasil per isolare database e API da internet pubblico, mentre il frontend web rimane accessibile pubblicamente tramite proxy sicuro.

### Componenti Principali
1. **Frontend Pubblico**: Sito web HTML/CSS/JS servito da un server web pubblico (es. Apache con HTTPS), che effettua chiamate AJAX a endpoint locali.
2. **Proxy Backend**: Server web configurato con proxy reverse (es. Apache ProxyPass) che inoltra richieste API a indirizzi IPv6 Yggdrasil privati.
3. **API Isolati**: Applicazione server scritta in Python con Flask, ospitata su un nodo Yggdrasil remoto, accessibile solo da altri nodi Yggdrasil. Include controlli di autenticazione (API key) e verifica di provenienza dalla rete Ygg (controllo se l'IP client è in 200::/8).
4. **Database Isolati**: Database relazionale SQLite ospitato sul nodo remoto Yggdrasil, accessibile solo via API isolati, con schema per utenti, pagamenti e dati applicativi.
5. **Rete Yggdrasil**: Overlay network decentralizzata che collega i nodi (PC locale, server remoto) senza passare per internet pubblico.

### Funzionamento
- L'utente accede al sito pubblico via browser.
- Il frontend chiama endpoint pubblici (es. /api/dipendenti).
- Il proxy sul server pubblico inoltra la richiesta all'IP Yggdrasil privato dell'API remota.
- L'API remota verifica che la richiesta provenga da Yggdrasil e risponde.
- Il proxy restituisce la risposta al frontend.

**Esempio Pratico**: L'utente aggiunge un dipendente. Flusso: Browser invia POST a /api/dipendenti → Apache proxy a http://[ygg-ip]:7123/api/dipendenti → API Flask verifica IP in 200::/8 e API key → Salva in SQLite → Risposta torna al browser.

### Vantaggi
- **Isolamento Completo**: Database e API non esposti a internet pubblico.
- **Sicurezza**: Comunicazioni crittografate e decentralizzate.
- **Scalabilità**: Facile aggiunta di nodi Yggdrasil.
- **Privacy**: Nessun indirizzo pubblico per backend.

## Figure
(Descrivere schematicamente con ASCII art)

**Figura 1: Architettura Generale**
```
Browser Pubblico (Internet)
    |
    v
Server Pubblico (Apache HTTPS)
    |
    +--> Proxy Reverse (/api/* -> Ygg IP)
    |
    v
Rete Yggdrasil (Decentralizzata, IPv6 200::/8)
    |
    v
Server Remoto (Flask API + SQLite DB)
```

**Figura 2: Flusso di Dati Isolato**
```
1. Browser: GET /api/key
2. Apache: Proxy -> Ygg IP /api/key
3. API: Verifica IP Ygg -> Restituisce chiave
4. Browser: POST /api/dipendenti con chiave
5. Apache: Proxy -> Ygg IP /api/dipendenti
6. API: Verifica chiave e IP Ygg -> Salva in DB -> Risposta
7. Browser: Mostra dati
```

## Rivendicazioni
1. Un sistema per isolamento sicuro di applicazioni web, comprendente: un frontend pubblico, un proxy configurato per inoltrare richieste a indirizzi Yggdrasil privati, un'API isolata in Yggdrasil con controlli di accesso, e un database accessibile solo via API.
2. Un metodo per proteggere backend web, comprendente i passi di: servire un frontend pubblico, proxy richieste API a indirizzi Yggdrasil, verificare provenienza da Yggdrasil nell'API, e isolare il database in Yggdrasil.
3. L'uso di Yggdrasil per isolamento di API web, come rivendicato.

## Data di Priorità
28 Ottobre 2025

## Inventore
Alex (principale inventore), con contributi da collaboratori nel progetto Site-Python.com.

Questo documento è una bozza preliminare per richiesta di brevetto. Consultare un avvocato specializzato per formalizzazione, ricerca di anteriorità e deposito presso l'ufficio brevetti competente (es. EPO o USPTO).

## Implementazione
Per implementare l'invenzione:
- **Configurazione Yggdrasil**: Installa Yggdrasil sui nodi, configura peer (es. tls://ip:port), genera chiavi pubbliche/private, limita AllowedPublicKeys per sicurezza.
- **Proxy Apache**: Nel VirtualHost, aggiungi `ProxyPass /api http://[ygg-ip]:porta/api` e `ProxyPassReverse /api http://[ygg-ip]:porta/api`. Abilita mod_proxy e mod_proxy_http.
- **API Flask**: Scrivi app con @app.before_request per controlli, endpoint per ottenere chiave dinamicamente (/api/key), e logica applicativa.
- **Database**: Usa SQLite con schema sicuro, accessibile solo via API.
- **Test**: Verifica isolamento chiamando da IP non-Ygg (dovrebbe fallire) e da Ygg (successo).

## Implementazione Completata e Testata
L'invenzione è stata implementata con successo nel progetto Site-Python.com:
- **Frontend Pubblico**: Sito HTTPS su Apache, con pagina dipendenti.html che chiama API via JavaScript.
- **Proxy Backend**: Apache configurato con ProxyPass per inoltrare /api a IP Yggdrasil privato.
- **API Isolati**: Flask app su server remoto Yggdrasil, con controlli IPv6 200::/8 e API key dinamica.
- **Database Isolati**: SQLite accessibile solo via API Ygg.
- **Test di Successo**: Curl e browser confermano isolamento sicuro; richieste da internet pubblico sono proxyate senza esporre Ygg al cliente.
- **Data di Completamento**: 28 Ottobre 2025.

Il sistema dimostra isolamento completo, sicurezza decentralizzata e scalabilità, superando soluzioni esistenti come VPN e Tor.
