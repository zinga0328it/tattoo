const puppeteer = require('puppeteer');

async function testFixHtmlModificato() {
    console.log('=== TEST FIX HTML MODIFICATO ===');
    
    const browser = await puppeteer.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    
    // User agent normale
    await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
    
    // Cookie autenticazione PRIMA del caricamento
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
        await dialog.accept('Test cancellazione con HTML modificato');
    });
    
    page.on('response', response => {
        if (response.url().includes('/works/') && response.request().method() === 'DELETE') {
            console.log('📥 DELETE RESPONSE:', response.url(), response.status());
        }
    });
    
    try {
        console.log('🔗 Caricamento pagina con fix integrato...');
        await page.goto('https://servicess.net/fibra/gestionale-ftth.html', { 
            waitUntil: 'networkidle2',
            timeout: 30000 
        });
        
        console.log('⏳ Attesa caricamento completo...');
        await new Promise(resolve => setTimeout(resolve, 8000));
        
        // Verifica che il fix sia attivo
        const isFixActive = await page.evaluate(() => {
            return window.mostraNote && window.mostraNote.toString().includes('CANCELLAZIONE ATTIVATA');
        });
        
        console.log('🔧 Fix attivo:', isFixActive);
        
        // Verifica pulsanti cancella
        const ordiniCaricati = await page.$$('.order-card');
        console.log(`📊 Ordini caricati: ${ordiniCaricati.length}`);
        
        const pulsantiCancella = await page.$$('.btn-annulla');
        console.log(`🗑️ Pulsanti cancella: ${pulsantiCancella.length}`);
        
        if (pulsantiCancella.length > 0) {
            console.log('✅ PULSANTI CANCELLA TROVATI - Testando cancellazione...');
            
            const orderCard = await pulsantiCancella[0].evaluateHandle(btn => btn.closest('.order-card'));
            const orderId = await orderCard.evaluate(card => card.dataset.orderId);
            console.log(`🎯 ID ordine: ${orderId}`);
            
            const ordiniPrima = await page.$$('.order-card');
            console.log(`📊 Ordini prima: ${ordiniPrima.length}`);
            
            // Clicca il pulsante cancella
            await pulsantiCancella[0].click();
            
            // Aspetta completamento
            await new Promise(resolve => setTimeout(resolve, 5000));
            
            const ordiniDopo = await page.$$('.order-card');
            console.log(`📊 Ordini dopo: ${ordiniDopo.length}`);
            
            if (ordiniDopo.length < ordiniPrima.length) {
                console.log('🎉 SUCCESSO: Cancellazione riuscita con HTML modificato!');
            } else {
                console.log('⚠️ Numero ordini invariato - controlla logs');
            }
            
        } else {
            console.log('❌ NESSUN PULSANTE CANCELLA');
        }
        
        // Verifica pulsante test
        const testButton = await page.$('button');
        if (testButton) {
            const buttonText = await testButton.evaluate(btn => btn.innerHTML);
            if (buttonText.includes('TEST CANCELLAZIONE')) {
                console.log('✅ PULSANTE TEST PRESENTE');
            }
        }
        
    } catch (e) {
        console.log('💥 ERRORE TEST:', e.message);
    } finally {
        await browser.close();
        console.log('🏁 Test completato');
    }
}

testFixHtmlModificato();
