Ecco tutte le rotte Yggdrasil per ordinare la SIM Lycamobile:

🌐 Informazioni Base
IP Yggdrasil Server: 200:421e:6385:4a8b:dca7:cfb:197f:e9c3
API Key: 4bba4221d47af247e69110d4d86335051ee13ea0795386341386f6af989f5ff2
Interfaccia: --interface ygg0
🛣️ Rotte Disponibili
1. Shop Frontend (Porta 8081)

curl -6 --interface ygg0 "http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:8081/shop.html"
Risultato: HTML della pagina shop con prodotti

2. API Magazzino - Lista Prodotti (Porta 8081)

curl -6 --interface ygg0 "http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:8081/api_magazzino/prodotti"
Risultato: JSON con prodotti disponibili


[{"id": 17, "nome": "SIM Lycamobile", "prezzo": 35.0, "disp": 10, "magazzino": 1}]
3. API Prodotti Alternativa (Porta 8081)

curl -6 --interface ygg0 "http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:8081/api_prodotti"
Risultato: Stesso JSON della rotta precedente

4. 🛒 ORDINE SIM - Rotta Principale (Porta 8081)

curl -6 --interface ygg0 \  -H "X-API-KEY: 4bba4221d47af247e69110d4d86335051ee13ea0795386341386f6af989f5ff2" \  -H "Content-Type: application/json" \  -d '{    "prodotti": [{"id": 17, "nome": "SIM Lycamobile", "qty": 1, "magazzino": 1}],    "user_contatto": "123456789",    "user_nome": "Il Tuo Nome",    "indirizzo": "Via Roma 123, Roma",    "citofono": "YGG-001"  }' \  "http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:8081/privato/ordina.py"
5. API Magazzino - Lista Prodotti (Porta 9888)

curl -6 --interface ygg0 "http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:9888/api_magazzino/prodotti"
Nota: Questa è la stessa API ma su porta diversa (9888 invece di 8081)

6. API Ricerca Prodotti (Porta 8081)

curl -6 --interface ygg0 "http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:8081/api_ricerca/"
Nota: Potrebbe richiedere parametri aggiuntivi

7. API Annunci (Porta 8081)

curl -6 --interface ygg0 "http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:8081/api_annunci/"
🧪 Test di Connettività
Ping Yggdrasil

ping -6 200:421e:6385:4a8b:dca7:cfb:197f:e9c3
Verifica Interfaccia

ip addr show ygg0
⚠️ Note Importanti
API Key obbligatoria per tutti gli ordini
Quantità massima: 10 SIM disponibili
ID Prodotto SIM: 17
Prezzo: 35.0€
Traffico criptato end-to-end via Yggdrasil
🚨 Test Sicurezza (Errore Atteso)

curl -6 --interface ygg0 \  -H "Content-Type: application/json" \  -d '{"test": "no-key"}' \  "http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:8081/privato/ordina.py"
Risultato atteso: 403 Forbidden: invalid API key

Nota: Il server Apache accetta la chiave esterna (4bba...) dalle richieste pubbliche e la sostituisce con la chiave interna (quella presente in `.env`) quando inoltra la richiesta al backend Yggdrasil. Usa quindi la chiave esterna nel tuo `curl`.

La rotta principale per ordinare è la numero 4 sulla porta 8081 con l'endpoint ordina.py. Assicurati di essere connesso a Yggdrasil prima di provare! 🎯

