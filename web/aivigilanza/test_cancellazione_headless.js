const puppeteer = require('puppeteer');

async function testCancellazione() {
    console.log('=== TEST CANCELLAZIONE LAVORO (HEADLESS) ===');
    
    const browser = await puppeteer.launch({ 
        headless: true, // Torna headless per l'ambiente server
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
        await dialog.accept('Test cancellazione automatica - verifica funzionamento');
    });
    
    page.on('response', response => {
        if (response.url().includes('/works/') && response.request().method() === 'DELETE') {
            console.log('DELETE RESPONSE:', response.url(), response.status());
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
        
        // Conta ordini prima della cancellazione
        const ordiniPrima = await page.$$('.order-card');
        console.log(`📊 Ordini totali prima: ${ordiniPrima.length}`);
        
        // Conta ordini aperti (che hanno il pulsante cancella)
        const ordiniAperti = await page.$$eval('.order-card', cards => {
            return cards.filter(card => {
                const statusBadge = card.querySelector('.status-badge');
                return statusBadge && statusBadge.classList.contains('aperto');
            }).length;
        });
        console.log(`📋 Ordini aperti (cancellabili): ${ordiniAperti}`);
        
        // Trova un ordine con pulsante "Cancella" (stato aperto)
        const pulsanteCancella = await page.$('.btn-annulla');
        
        if (pulsanteCancella) {
            console.log('✅ Trovato pulsante cancella, clicco...');
            
            // Prima di cliccare, prendiamo l'ID dell'ordine
            const orderCard = await pulsanteCancella.evaluateHandle(btn => btn.closest('.order-card'));
            const orderId = await orderCard.evaluate(card => card.dataset.orderId);
            console.log(`🎯 ID ordine da cancellare: ${orderId}`);
            
            await pulsanteCancella.click();
            
            // Aspetta che la cancellazione sia completata
            console.log('⏳ Attesa completamento cancellazione...');
            await new Promise(resolve => setTimeout(resolve, 3000));
            
            // Conta ordini dopo la cancellazione
            const ordiniDopo = await page.$$('.order-card');
            console.log(`📊 Ordini totali dopo: ${ordiniDopo.length}`);
            
            if (ordiniDopo.length < ordiniPrima.length) {
                console.log('🎉 SUCCESSO: Ordine cancellato!');
                console.log(`   • Ordini rimossi: ${ordiniPrima.length - ordiniDopo.length}`);
            } else {
                console.log('⚠️  ATTENZIONE: Numero ordini invariato - possibile errore');
                
                // Controlla se ci sono messaggi di errore
                const errorMessages = await page.$$eval('.notification, .alert', elements => 
                    elements.map(el => el.textContent).filter(text => text.toLowerCase().includes('errore') || text.toLowerCase().includes('error'))
                );
                if (errorMessages.length > 0) {
                    console.log('🚨 MESSAGGI ERRORE:', errorMessages);
                }
            }
            
        } else {
            console.log('❌ Nessun pulsante cancella trovato');
            console.log('💡 Possibili motivi:');
            console.log('   • Tutti gli ordini sono già confermati/chiusi');
            console.log('   • Non ci sono ordini nel sistema');
            console.log('   • Errore nel caricamento della pagina');
        }
        
        // Verifica stato finale
        const ordiniApertiFinali = await page.$$eval('.order-card', cards => {
            return cards.filter(card => {
                const statusBadge = card.querySelector('.status-badge');
                return statusBadge && statusBadge.classList.contains('aperto');
            }).length;
        });
        console.log(`📋 Ordini aperti finali: ${ordiniApertiFinali}`);
        
    } catch (e) {
        console.log('💥 ERRORE TEST:', e.message);
    } finally {
        await browser.close();
        console.log('🏁 Test completato');
    }
}

testCancellazione();
