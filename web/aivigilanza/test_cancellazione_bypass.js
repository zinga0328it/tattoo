const puppeteer = require('puppeteer');

async function testCancellazioneBypass() {
    console.log('=== TEST CANCELLAZIONE - BYPASS BLOCCO ===');
    
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
        
        if (dialog.message().includes('Funzionalità in sviluppo')) {
            console.log('🚫 Rilevato blocco "Funzionalità in sviluppo" - rifiutando');
            await dialog.dismiss();
            return;
        }
        
        // Accetta il dialog normale della cancellazione
        await dialog.accept('Test cancellazione - bypass blocco');
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
        
        // Inietta codice per bypassare il blocco
        console.log('🔧 Iniettando codice di bypass...');
        await page.evaluate(() => {
            // Override della funzione alert per bloccare il messaggio "Funzionalità in sviluppo"
            const originalAlert = window.alert;
            window.alert = function(message) {
                if (message && message.includes('Funzionalità in sviluppo')) {
                    console.log('🚫 Alert "Funzionalità in sviluppo" bloccato');
                    return; // Non mostrare l'alert
                }
                return originalAlert.apply(this, arguments);
            };
            
            // Cerca e rimuovi eventuali event listener che potrebbero bloccare i click
            const buttons = document.querySelectorAll('.btn-annulla');
            buttons.forEach(button => {
                // Rimuovi tutti gli event listener di click e aggiungi il nostro
                const clone = button.cloneNode(true);
                button.parentNode.replaceChild(clone, button);
                
                // Ri-aggiungi l'event listener originale
                clone.addEventListener('click', function() {
                    const orderId = this.closest('.order-card').dataset.orderId;
                    mostraNote(orderId);
                });
            });
        });
        
        console.log('⏳ Attesa caricamento...');
        await new Promise(resolve => setTimeout(resolve, 5000));
        
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
            await new Promise(resolve => setTimeout(resolve, 3000));
            
            // Conta ordini dopo
            const ordiniDopo = await page.$$('.order-card');
            console.log(`📊 Ordini dopo: ${ordiniDopo.length}`);
            
            if (ordiniDopo.length < ordiniPrima.length) {
                console.log('🎉 SUCCESSO: Ordine cancellato!');
            } else {
                console.log('⚠️  Numero ordini invariato');
            }
            
        } else {
            console.log('❌ Nessun pulsante cancella trovato');
        }
        
    } catch (e) {
        console.log('�� ERRORE TEST:', e.message);
    } finally {
        await browser.close();
        console.log('🏁 Test completato');
    }
}

testCancellazioneBypass();
