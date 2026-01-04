const puppeteer = require('puppeteer');

async function testCancellazione() {
    console.log('=== TEST CANCELLAZIONE LAVORO ===');
    
    const browser = await puppeteer.launch({ 
        headless: false, // Visibile per vedere cosa succede
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
        // Inserisci automaticamente una nota di test
        await dialog.accept('Test cancellazione automatica');
    });
    
    try {
        console.log('🔗 Caricamento pagina...');
        await page.goto('https://servicess.net/fibra/gestionale-ftth.html', { 
            waitUntil: 'networkidle2',
            timeout: 30000 
        });
        
        console.log('⏳ Attesa caricamento...');
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Conta ordini prima della cancellazione
        const ordiniPrima = await page.$$('.order-card');
        console.log(`📊 Ordini prima: ${ordiniPrima.length}`);
        
        // Trova un ordine con pulsante "Cancella" (stato aperto)
        const pulsanteCancella = await page.$('.btn-annulla');
        
        if (pulsanteCancella) {
            console.log('✅ Trovato pulsante cancella, clicco...');
            await pulsanteCancella.click();
            
            // Aspetta che la cancellazione sia completata
            await new Promise(resolve => setTimeout(resolve, 3000));
            
            // Conta ordini dopo la cancellazione
            const ordiniDopo = await page.$$('.order-card');
            console.log(`📊 Ordini dopo: ${ordiniDopo.length}`);
            
            if (ordiniDopo.length < ordiniPrima.length) {
                console.log('🎉 SUCCESSO: Ordine cancellato!');
            } else {
                console.log('⚠️  ATTENZIONE: Numero ordini invariato');
            }
            
        } else {
            console.log('❌ Nessun pulsante cancella trovato (nessun ordine aperto)');
        }
        
    } catch (e) {
        console.log('💥 ERRORE TEST:', e.message);
    } finally {
        // Aspetta un po' prima di chiudere per vedere il risultato
        await new Promise(resolve => setTimeout(resolve, 5000));
        await browser.close();
        console.log('🏁 Test completato');
    }
}

testCancellazione();
