const puppeteer = require('puppeteer');

async function testCancellazioneDebug() {
    console.log('=== TEST CANCELLAZIONE CON DEBUG ===');
    
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
    
    // Intercetta tutte le richieste per debug
    await page.setRequestInterception(true);
    
    page.on('request', request => {
        const url = request.url();
        if (url.includes('/works/') && request.method() === 'DELETE') {
            console.log('🚨 DELETE REQUEST INTERCEPTED:');
            console.log('   URL:', url);
            console.log('   Method:', request.method());
            console.log('   Headers:', JSON.stringify(request.headers(), null, 2));
            console.log('   Body:', request.postData());
        }
        request.continue();
    });
    
    page.on('response', response => {
        const url = response.url();
        if (url.includes('/works/') && response.request().method() === 'DELETE') {
            console.log('📥 DELETE RESPONSE:');
            console.log('   URL:', url);
            console.log('   Status:', response.status());
            console.log('   Headers:', JSON.stringify(response.headers(), null, 2));
        }
    });
    
    page.on('console', msg => {
        console.log('CONSOLE:', msg.text());
    });
    
    page.on('dialog', async dialog => {
        console.log('DIALOG:', dialog.message());
        
        // Se è il dialog di "Funzionalità in sviluppo", rifiutalo
        if (dialog.message().includes('Funzionalità in sviluppo')) {
            console.log('🚫 Rifiutando dialog "Funzionalità in sviluppo"');
            await dialog.dismiss();
            return;
        }
        
        // Altrimenti accetta con una nota
        await dialog.accept('Test cancellazione - debug API');
    });
    
    try {
        console.log('🔗 Caricamento pagina...');
        await page.goto('https://servicess.net/fibra/gestionale-ftth.html', { 
            waitUntil: 'networkidle2',
            timeout: 30000 
        });
        
        console.log('⏳ Attesa caricamento...');
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Trova un ordine con pulsante "Cancella"
        const pulsanteCancella = await page.$('.btn-annulla');
        
        if (pulsanteCancella) {
            console.log('✅ Trovato pulsante cancella, clicco...');
            
            const orderCard = await pulsanteCancella.evaluateHandle(btn => btn.closest('.order-card'));
            const orderId = await orderCard.evaluate(card => card.dataset.orderId);
            console.log(`🎯 ID ordine da cancellare: ${orderId}`);
            
            await pulsanteCancella.click();
            
            // Aspetta che eventuali dialog siano gestiti
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Aspetta che la cancellazione sia completata
            console.log('⏳ Attesa completamento...');
            await new Promise(resolve => setTimeout(resolve, 3000));
            
            // Verifica risultato
            const ordiniDopo = await page.$$('.order-card');
            console.log(`📊 Ordini dopo tentativo cancellazione: ${ordiniDopo.length}`);
            
            // Controlla notifiche
            const notifications = await page.$$eval('.notification', elements => 
                elements.map(el => el.textContent)
            );
            console.log('🔔 Notifiche:', notifications);
            
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

testCancellazioneDebug();
