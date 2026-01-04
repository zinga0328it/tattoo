// FIX COMPLETO PER CANCELLAZIONE FTTH
// Da copiare nella console del browser (F12 -> Console)

(function() {
    console.log('🔧 APPLICANDO FIX COMPLETO CANCELLAZIONE...');
    
    // 1. BLOCCA TUTTI GLI ALERT CHE CONTENGONO "Funzionalità in sviluppo"
    const originalAlert = window.alert;
    window.alert = function(message) {
        if (message && typeof message === 'string' && message.includes('Funzionalità in sviluppo')) {
            console.log('🚫 ALERT BLOCCATO:', message);
            return false;
        }
        console.log('✅ ALERT PERMESSO:', message);
        return originalAlert.apply(this, arguments);
    };
    
    // 2. IMPOSTA COOKIE AUTENTICAZIONE SE NECESSARIO
    function setAuthCookie() {
        const cookies = document.cookie.split(';');
        const hasAuth = cookies.some(cookie => cookie.trim().startsWith('ftth_auth='));
        
        if (!hasAuth) {
            console.log('🍪 IMPOSTANDO COOKIE AUTENTICAZIONE...');
            document.cookie = 'ftth_auth=true; path=/; domain=servicess.net; secure; samesite=none';
        } else {
            console.log('✅ COOKIE AUTENTICAZIONE GIÀ PRESENTE');
        }
    }
    
    // 3. SOVRASCRIVI COMPLETAMENTE LA FUNZIONE mostraNote
    window.mostraNote = async function(orderId) {
        console.log('=== CANCELLAZIONE INIZIATA ===');
        console.log('Order ID:', orderId);
        
        try {
            // Verifica autenticazione
            setAuthCookie();
            
            // Chiedi motivo cancellazione
            const note = prompt('Inserisci il motivo della cancellazione:');
            console.log('Nota inserita:', note);
            
            if (!note || !note.trim()) {
                console.log('❌ CANCELLAZIONE ANNULLATA: nota vuota');
                alert('Cancellazione annullata: devi inserire un motivo');
                return;
            }
            
            console.log('📤 INVIO RICHIESTA DELETE...');
            
            // Costruisci URL API
            const apiUrl = `https://servicess.net/gestionale/works/${orderId}`;
            console.log('API URL:', apiUrl);
            
            // Prepara richiesta
            const requestData = {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': 'JHzxUzdAK8LJ33Y50MDgLf5E62flYset4MYA6ELpXpU='
                },
                body: JSON.stringify({ 
                    note_cancellazione: note.trim() 
                })
            };
            console.log('Request data:', requestData);
            
            // Invia richiesta
            const response = await fetch(apiUrl, requestData);
            console.log('Response status:', response.status);
            console.log('Response headers:', [...response.headers.entries()]);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('❌ ERRORE API:', response.status, errorText);
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            
            const result = await response.text();
            console.log('✅ SUCCESSO:', result);
            
            // Ricarica ordini
            if (typeof loadOrders === 'function') {
                console.log('🔄 RICARICANDO ORDINI...');
                await loadOrders();
            }
            
            // Mostra notifica
            if (typeof showNotification === 'function') {
                showNotification('Lavoro cancellato con successo!', 'success');
            } else {
                alert('✅ Lavoro cancellato con successo!');
            }
            
            console.log('=== CANCELLAZIONE COMPLETATA ===');
            
        } catch (error) {
            console.error('💥 ERRORE CANCELLAZIONE:', error);
            
            // Mostra errore
            if (typeof showNotification === 'function') {
                showNotification(`Errore cancellazione: ${error.message}`, 'error');
            } else {
                alert(`❌ Errore: ${error.message}`);
            }
            
            console.log('=== CANCELLAZIONE FALLITA ===');
        }
    };
    
    // 4. AGGIUNGI LOGGING AI PULSANTI CANCELLA
    function enhanceCancelButtons() {
        console.log('🔍 CERCO PULSANTI CANCELLA...');
        const cancelButtons = document.querySelectorAll('.btn-annulla');
        console.log('Trovati', cancelButtons.length, 'pulsanti cancella');
        
        cancelButtons.forEach((btn, index) => {
            btn.addEventListener('click', function(e) {
                console.log(`🖱️ CLICCATO PULSANTE CANCELLA #${index + 1}`);
                const orderCard = this.closest('.order-card');
                if (orderCard) {
                    const orderId = orderCard.dataset.orderId;
                    console.log('Order ID dal dataset:', orderId);
                }
            });
        });
    }
    
    // 5. APPLICA FIX AL CARICAMENTO
    setAuthCookie();
    enhanceCancelButtons();
    
    // 6. MONITORA CAMBIAMENTI DOM (per ordini dinamici)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                enhanceCancelButtons();
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    console.log('✅ FIX COMPLETO APPLICATO!');
    console.log('🎯 Ora puoi provare a cancellare un ordine cliccando "Cancella"');
    
    // Test immediato
    setTimeout(() => {
        console.log('🧪 TEST: cercando pulsanti cancella...');
        const testButtons = document.querySelectorAll('.btn-annulla');
        if (testButtons.length > 0) {
            console.log(`✅ TROVATI ${testButtons.length} PULSANTI CANCELLA`);
        } else {
            console.log('⚠️ NESSUN PULSANTE CANCELLA TROVATO - ricarica la pagina');
        }
    }, 1000);
    
})();