const puppeteer = require('puppeteer');

async function testFixCookiePrima() {
    console.log('=== TEST FIX - Cookie impostato PRIMA del caricamento ===');
    
    const browser = await puppeteer.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    
    // User agent normale
    await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
    
    // IMPOSTA COOKIE PRIMA DI CARICARE LA PAGINA
    console.log('🍪 Impostando cookie autenticazione PRIMA del caricamento...');
    await page.setCookie({
        name: 'ftth_auth',
        value: 'true',
        domain: 'servicess.net',
        path: '/',
        httpOnly: false,
        secure: true,
        sameSite: 'None'
    });
    
    page.on('console', msg => {
        console.log('CONSOLE:', msg.text());
    });
    
    page.on('dialog', async dialog => {
        console.log('DIALOG:', dialog.message());
        // Simula l'utente che inserisce una nota
        await dialog.accept('Test cancellazione con cookie pre-impostato');
    });
    
    page.on('response', response => {
        if (response.url().includes('/works/')) {
            console.log('📥 API RESPONSE:', response.request().method(), response.url(), response.status());
        }
    });
    
    try {
        console.log('🔗 Caricamento pagina con cookie già impostato...');
        await page.goto('https://servicess.net/fibra/gestionale-ftth.html', { 
            waitUntil: 'networkidle2',
            timeout: 30000 
        });
        
        console.log('⏳ Attesa caricamento ordini...');
        await new Promise(resolve => setTimeout(resolve, 8000)); // Più tempo per caricamento
        
        // Verifica che ci siano ordini
        const ordiniCaricati = await page.$$('.order-card');
        console.log(`📊 Ordini caricati: ${ordiniCaricati.length}`);
        
        if (ordiniCaricati.length === 0) {
            console.log('❌ NESSUN ORDINE CARICATO - Problema autenticazione o API');
            
            // Controlla se c'è un errore nella console
            const consoleMessages = [];
            page.on('console', msg => {
                consoleMessages.push(msg.text());
            });
            
            // Riprova a caricare gli ordini manualmente
            console.log('🔄 Tentativo ricarica manuale ordini...');
            await page.evaluate(() => {
                if (typeof loadOrders === 'function') {
                    loadOrders();
                }
            });
            
            await new Promise(resolve => setTimeout(resolve, 3000));
            
            const ordiniDopoRicarica = await page.$$('.order-card');
            console.log(`📊 Ordini dopo ricarica manuale: ${ordiniDopoRicarica.length}`);
            
            if (ordiniDopoRicarica.length === 0) {
                console.log('💥 IMPOSSIBILE CARICARE ORDINI - Controlla autenticazione');
                return;
            }
        }
        
        // Ora applica il fix
        console.log('🔧 Applicando fix completo...');
        await page.evaluate(() => {
            (function() {
                console.log('🔧 APPLICANDO FIX COMPLETO CANCELLAZIONE...');
                
                const originalAlert = window.alert;
                window.alert = function(message) {
                    if (message && typeof message === 'string' && message.includes('Funzionalità in sviluppo')) {
                        console.log('🚫 ALERT BLOCCATO:', message);
                        return false;
                    }
                    return originalAlert.apply(this, arguments);
                };
                
                window.mostraNote = async function(orderId) {
                    console.log('=== CANCELLAZIONE INIZIATA ===');
                    console.log('Order ID:', orderId);
                    
                    try {
                        const note = prompt('Motivo:');
                        if (!note || !note.trim()) {
                            alert('Nota obbligatoria');
                            return;
                        }
                        
                        const response = await fetch(`https://servicess.net/gestionale/works/${orderId}`, {
                            method: 'DELETE',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-API-Key': 'JHzxUzdAK8LJ33Y50MDgLf5E62flYset4MYA6ELpXpU='
                            },
                            body: JSON.stringify({ note_cancellazione: note.trim() })
                        });
                        
                        if (!response.ok) {
                            throw new Error(`HTTP ${response.status}`);
                        }
                        
                        const result = await response.text();
                        console.log('SUCCESSO:', result);
                        
                        if (typeof loadOrders === 'function') {
                            await loadOrders();
                        }
                        
                        if (typeof showNotification === 'function') {
                            showNotification('Cancellato!', 'success');
                        } else {
                            alert('✅ Cancellato!');
                        }
                        
                    } catch (error) {
                        console.error('ERRORE:', error);
                        alert('Errore: ' + error.message);
                    }
                };
                
                console.log('✅ FIX APPLICATO');
            })();
        });
        
        // Ora testa la cancellazione
        const pulsanteCancella = await page.$('.btn-annulla');
        
        if (pulsanteCancella) {
            console.log('✅ Trovato pulsante cancella, testando...');
            
            const orderCard = await pulsanteCancella.evaluateHandle(btn => btn.closest('.order-card'));
            const orderId = await orderCard.evaluate(card => card.dataset.orderId);
            console.log(`🎯 ID ordine: ${orderId}`);
            
            const ordiniPrima = await page.$$('.order-card');
            console.log(`📊 Ordini prima: ${ordiniPrima.length}`);
            
            await pulsanteCancella.click();
            
            await new Promise(resolve => setTimeout(resolve, 5000));
            
            const ordiniDopo = await page.$$('.order-card');
            console.log(`📊 Ordini dopo: ${ordiniDopo.length}`);
            
            if (ordiniDopo.length < ordiniPrima.length) {
                console.log('🎉 SUCCESSO: Cancellazione riuscita!');
            } else {
                console.log('⚠️ Cancellazione non completata');
            }
            
        } else {
            console.log('❌ Nessun pulsante cancella disponibile');
        }
        
    } catch (e) {
        console.log('💥 ERRORE TEST:', e.message);
    } finally {
        await browser.close();
        console.log('🏁 Test completato');
    }
}

testFixCookiePrima();
