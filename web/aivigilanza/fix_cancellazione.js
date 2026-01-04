// Script per abilitare la cancellazione nel browser
// Copia e incolla questo codice nella console del browser (F12) quando sei sulla pagina gestionale-ftth.html

// 1. Override della funzione alert per bloccare il messaggio "Funzionalità in sviluppo"
const originalAlert = window.alert;
window.alert = function(message) {
    if (message && message.includes('Funzionalità in sviluppo')) {
        console.log('🚫 Bloccato alert "Funzionalità in sviluppo"');
        return false;
    }
    return originalAlert.apply(this, arguments);
};

// 2. Modifica della funzione mostraNote per funzionare correttamente
const originalMostraNote = window.mostraNote;
window.mostraNote = async function(orderId) {
    console.log('=== CANCELLAZIONE ABILITATA ===');
    console.log('Order ID:', orderId);
    
    // Chiedi il motivo della cancellazione
    const note = prompt('Motivo cancellazione:');
    console.log('Nota inserita:', note);
    
    if (note && note.trim()) {
        try {
            console.log('Invio richiesta DELETE...');
            const response = await apiFetch(`/works/${orderId}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ note_cancellazione: note })
            });

            console.log('Risposta ricevuta:', response.status, response.statusText);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.text();
            console.log('Risposta body:', result);

            await loadOrders();
            showNotification('Lavoro cancellato con successo', 'success');
            console.log('=== CANCELLAZIONE COMPLETATA ===');
        } catch (e) {
            console.error('Errore cancellazione:', e);
            showNotification(`Errore nella cancellazione: ${e.message}`, 'error');
            console.log('=== CANCELLAZIONE FALLITA ===');
        }
    } else {
        console.log('Cancellazione annullata - nota vuota');
    }
};

console.log('✅ CANCELLAZIONE ABILITATA!');
console.log('Ora puoi cliccare sui pulsanti "✗ Cancella" per rimuovere i lavori.');
