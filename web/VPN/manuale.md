✅ COMANDO CURL COMPLETO PER ORDINARE LA SIM MANUALMENTE
Dal tuo PC remoto connesso a Yggdrasil, copia e incolla questo comando completo nel terminale:


curl -6 --interface ygg0 \  -H "X-API-KEY: 4bba4221d47af247e69110d4d86335051ee13ea0795386341386f6af989f5ff2" \  -H "Content-Type: application/json" \  -d '{    "prodotti": [{"id": 17, "nome": "SIM Lycamobile", "qty": 1, "magazzino": 1}],    "user_contatto": "IL_TUO_ID_TELEGRAM_NUMERICO",    "user_nome": "Il Tuo Nome",    "indirizzo": "Via Roma 123, Roma",    "citofono": "YGG-001"  }' \  "http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:8081/privato/ordina.py"
📝 MODIFICHE DA FARE:
Sostituisci "IL_TUO_ID_TELEGRAM_NUMERICO" con il tuo ID Telegram numerico
Modifica "Il Tuo Nome" con il tuo nome reale
Cambia indirizzo e citofono con i tuoi dati di consegna
🎯 Esempio Concreto:

curl -6 --interface ygg0 \  -H "X-API-KEY: 4bba4221d47af247e69110d4d86335051ee13ea0795386341386f6af989f5ff2" \  -H "Content-Type: application/json" \  -d '{    "prodotti": [{"id": 17, "nome": "SIM Lycamobile", "qty": 1, "magazzino": 1}],    "user_contatto": "123456789",    "user_nome": "Mario Rossi",    "indirizzo": "Via Garibaldi 45, Milano",    "citofono": "ROSSI-2B"  }' \  "http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:8081/privato/ordina.py"
📱 RISULTATO ATTESO:

{  "ordine": 66,  "admin_ok": ["7586394272"],  "corrieri_ok": [],  "client_ok": "123456789",  "client_failed": null,  "messaggio": "Ordine n. 66 ricevuto. Notifiche: admin ok=1 corrieri ok=0"}
🚨 IMPORTANTE:
Assicurati di essere connesso a Yggdrasil prima di eseguire il comando
Riceverai conferma su Telegram all'ID che hai inserito
L'ordine sarà visibile nel sistema di tracciamento
Copia il comando, modifica i tuoi dati e eseguilo! 🎯🔐

Nota: Apache sul sito pubblico verifica la chiave esterna (quella mostrata sopra) e la sostituisce automaticamente con la chiave interna del server prima di inoltrare la richiesta al backend. Quindi nelle tue richieste curl usa la chiave esterna (4bba...); Apache provvederà a inviare la chiave interna (quella definita sul server) al servizio Yggdrasil.