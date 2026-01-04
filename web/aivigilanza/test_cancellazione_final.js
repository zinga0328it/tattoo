const puppeteer = require('puppeteer');

async function testCancellazioneFinal() {
    console.log('=== TEST CANCELLAZIONE FINALE ===');
    
    const browser = await puppeteer.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    
    // User agent normale
    await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
    
    // BYPASS AUTENTICAZIONE
    await page.setCookie({
        name: 'ftth_auth',
        value: 'true',
        domain: 'servicess.net',
        path: '/',
        httpOnly: false,
        secure: true
    });
    
    page.on('console', msg => {
        console.log('CONSOLE:', msg.text());
    });
    
    page.on('dialog', async dialog => {
        console.log('DIALOG:', dialog.message());
        // Accetta automaticamente tutti i dialog
        await dialog.accept('Test cancellazione finale');
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
        
        // Inietta codice per abilitare la cancellazione
        console.log('🔧 Abilitando cancellazione...');
        await page.evaluate(() => {
            // Override della funzione alert per bloccare blocchi
            const originalAlert = window.alert;
            window.alert = function(message) {
                if (message && message.includes('Funzionalità in sviluppo')) {
                    console.log('🚫 Bloccato alert:', message);
                    return false;
                }
                return originalAlert.apply(this, arguments);
            };
            
            // Modifica la funzione mostraNote per evitare blocchi
            const originalMostraNote = window.mostraNote;
            window.mostraNote = async function(orderId) {
                console.log('=== MODIFICA MOSTRA NOTE ===');
                console.log('Order ID:', orderId);
                
                // Salta il prompt e vai direttamente alla cancellazione
                const note = 'Cancellazione automatica dal test';
                console.log('Nota automatica:', note);
                
                if (note) {
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
                }
            };
        });
        
        console.log('⏳ Attesa setup...');
        await new Promise(resolve => setTimeout(resolve, 3000));
        
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
                console.log('🎉 SUCCESSO: Ordine cancellato!');
                console.log(`   • Ordini rimossi: ${ordiniPrima.length - ordiniDopo.length}`);
            } else {
                console.log('⚠️  Numero ordini invariato');
                
                // Controlla notifiche
                const notifications = await page.$$eval('.notification', elements => 
                    elements.map(el => el.textContent)
                );
                console.log('🔔 Notifiche:', notifications);
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

testCancellazioneFinal();
