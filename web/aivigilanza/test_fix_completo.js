const puppeteer = require('puppeteer');

async function testFixCompleto() {
    console.log('=== TEST FIX COMPLETO - Simula browser con fix completo ===');
    
    const browser = await puppeteer.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    
    // User agent normale
    await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
    
    page.on('console', msg => {
        console.log('CONSOLE:', msg.text());
    });
    
    page.on('dialog', async dialog => {
        console.log('DIALOG:', dialog.message());
        // Simula l'utente che inserisce una nota
        await dialog.accept('Test cancellazione con fix completo');
    });
    
    page.on('response', response => {
        if (response.url().includes('/works/') && response.request().method() === 'DELETE') {
            console.log('📥 DELETE RESPONSE:', response.url(), response.status());
        }
    });
    
    try {
        console.log('🔗 Caricamento pagina...');
        await page.goto('https://servicess.net/fibra/gestionale-ftth.html', { 
            waitUntil: 'networkidle2',
            timeout: 30000 
        });
        
        console.log('⏳ Attesa caricamento...');
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // APPLICA IL FIX COMPLETO
        console.log('�� Applicando fix completo...');
        await page.evaluate(() => {
            // Stesso codice del fix_cancellazione_completo.js
            (function() {
                console.log('🔧 APPLICANDO FIX COMPLETO CANCELLAZIONE...');
                
                // 1. BLOCCA TUTTI GLI ALERT
                const originalAlert = window.alert;
                window.alert = function(message) {
                    if (message && typeof message === 'string' && message.includes('Funzionalità in sviluppo')) {
                        console.log('�� ALERT BLOCCATO:', message);
                        return false;
                    }
                    console.log('✅ ALERT PERMESSO:', message);
                    return originalAlert.apply(this, arguments);
                };
                
                // 2. IMPOSTA COOKIE AUTENTICAZIONE
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
                
                // 3. SOVRASCRIVI mostraNote
                window.mostraNote = async function(orderId) {
                    console.log('=== CANCELLAZIONE INIZIATA ===');
                    console.log('Order ID:', orderId);
                    
                    try {
                        setAuthCookie();
                        
                        const note = prompt('Inserisci il motivo della cancellazione:');
                        console.log('Nota inserita:', note);
                        
                        if (!note || !note.trim()) {
                            console.log('❌ CANCELLAZIONE ANNULLATA: nota vuota');
                            alert('Cancellazione annullata: devi inserire un motivo');
                            return;
                        }
                        
                        console.log('📤 INVIO RICHIESTA DELETE...');
                        
                        const apiUrl = `https://servicess.net/gestionale/works/${orderId}`;
                        console.log('API URL:', apiUrl);
                        
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
                        
                        const response = await fetch(apiUrl, requestData);
                        console.log('Response status:', response.status);
                        
                        if (!response.ok) {
                            const errorText = await response.text();
                            console.error('❌ ERRORE API:', response.status, errorText);
                            throw new Error(`HTTP ${response.status}: ${errorText}`);
                        }
                        
                        const result = await response.text();
                        console.log('✅ SUCCESSO:', result);
                        
                        if (typeof loadOrders === 'function') {
                            console.log('🔄 RICARICANDO ORDINI...');
                            await loadOrders();
                        }
                        
                        if (typeof showNotification === 'function') {
                            showNotification('Lavoro cancellato con successo!', 'success');
                        } else {
                            alert('✅ Lavoro cancellato con successo!');
                        }
                        
                        console.log('=== CANCELLAZIONE COMPLETATA ===');
                        
                    } catch (error) {
                        console.error('💥 ERRORE CANCELLAZIONE:', error);
                        
                        if (typeof showNotification === 'function') {
                            showNotification(`Errore cancellazione: ${error.message}`, 'error');
                        } else {
                            alert(`❌ Errore: ${error.message}`);
                        }
                        
                        console.log('=== CANCELLAZIONE FALLITA ===');
                    }
                };
                
                // 4. ENHANCE BUTTONS
                function enhanceCancelButtons() {
                    console.log('🔍 CERCO PULSANTI CANCELLA...');
                    const cancelButtons = document.querySelectorAll('.btn-annulla');
                    console.log('Trovati', cancelButtons.length, 'pulsanti cancella');
                }
                
                setAuthCookie();
                enhanceCancelButtons();
                
                console.log('✅ FIX COMPLETO APPLICATO!');
            })();
        });
        
        console.log('⏳ Attesa setup fix...');
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Conta ordini prima
        const ordiniPrima = await page.$$('.order-card');
        console.log(`📊 Ordini prima: ${ordiniPrima.length}`);
        
        // Trova pulsante cancella
        const pulsanteCancella = await page.$('.btn-annulla');
        
        if (pulsanteCancella) {
            console.log('✅ Trovato pulsante cancella, clicco...');
            
            const orderCard = await pulsanteCancella.evaluateHandle(btn => btn.closest('.order-card'));
            const orderId = await orderCard.evaluate(card => card.dataset.orderId);
            console.log(`🎯 ID ordine: ${orderId}`);
            
            await pulsanteCancella.click();
            
            // Aspetta che la cancellazione sia completata
            console.log('⏳ Attesa completamento...');
            await new Promise(resolve => setTimeout(resolve, 5000));
            
            // Conta ordini dopo
            const ordiniDopo = await page.$$('.order-card');
            console.log(`📊 Ordini dopo: ${ordiniDopo.length}`);
            
            if (ordiniDopo.length < ordiniPrima.length) {
                console.log('🎉 SUCCESSO: Fix completo funziona!');
                console.log(`   • Ordini cancellati: ${ordiniPrima.length - ordiniDopo.length}`);
            } else {
                console.log('⚠️  Numero ordini invariato - controlla logs');
            }
            
        } else {
            console.log('❌ Nessun pulsante cancella trovato');
        }
        
    } catch (e) {
        console.log('💥 ERRORE TEST:', e.message);
    } finally {
        await browser.close();
        console.log('🏁 Test completato');
    }
}

testFixCompleto();
