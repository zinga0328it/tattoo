const puppeteer = require('puppeteer');

async function testCancellazioneAccept() {
    console.log('=== TEST CANCELLAZIONE - ACCETTA ENTRAMBI DIALOG ===');
    
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
    
    let dialogCount = 0;
    
    page.on('console', msg => {
        console.log('CONSOLE:', msg.text());
    });
    
    page.on('dialog', async dialog => {
        dialogCount++;
        console.log(`DIALOG ${dialogCount}:`, dialog.message());
        
        // Accetta tutti i dialog con una nota
        await dialog.accept('Test cancellazione - accetta tutti i dialog');
        console.log(`✅ Accettato dialog ${dialogCount}`);
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
            
            // Aspetta che tutti i dialog siano gestiti
            console.log('⏳ Attesa gestione dialog...');
            await new Promise(resolve => setTimeout(resolve, 3000));
            
            // Conta ordini dopo
            const ordiniDopo = await page.$$('.order-card');
            console.log(`📊 Ordini dopo: ${ordiniDopo.length}`);
            console.log(`📊 Dialog gestiti: ${dialogCount}`);
            
            if (ordiniDopo.length < ordiniPrima.length) {
                console.log('🎉 SUCCESSO: Ordine cancellato!');
            } else {
                console.log('⚠️  Numero ordini invariato');
                
                // Controlla notifiche di errore
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

testCancellazioneAccept();
