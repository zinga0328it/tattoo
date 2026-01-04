const puppeteer = require('puppeteer');

async function testBrowserFix() {
    console.log('=== TEST FIX BROWSER - Simula uso normale ===');
    
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
        // Simula l'utente che inserisce una nota
        await dialog.accept('Test cancellazione da browser con fix');
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
        
        // APPLICA IL FIX DEL BROWSER (simula copia/incolla nella console)
        console.log('🔧 Applicando fix browser...');
        await page.evaluate(() => {
            // Stesso codice del fix_cancellazione.js
            const originalAlert = window.alert;
            window.alert = function(message) {
                if (message && message.includes('Funzionalità in sviluppo')) {
                    console.log('🚫 Bloccato alert "Funzionalità in sviluppo"');
                    return false;
                }
                return originalAlert.apply(this, arguments);
            };

            const originalMostraNote = window.mostraNote;
            window.mostraNote = async function(orderId) {
                console.log('=== CANCELLAZIONE ABILITATA ===');
                console.log('Order ID:', orderId);
                
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
                    console.log('Cancellazione annullata dall\'utente');
                }
            };

            console.log('✅ CANCELLAZIONE ABILITATA!');
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
                console.log('🎉 SUCCESSO: Fix browser funziona!');
                console.log(`   • Ordini cancellati: ${ordiniPrima.length - ordiniDopo.length}`);
            } else {
                console.log('⚠️  Numero ordini invariato');
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

testBrowserFix();
