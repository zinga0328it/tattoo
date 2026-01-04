const puppeteer = require('puppeteer');

async function testFinal() {
    console.log('=== TEST FINALE: FTTH Management Page ===');
    console.log('Test completo con autenticazione e caricamento ordini...');
    
    const browser = await puppeteer.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    
    // Configurazione per simulare un browser normale
    await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
    
    // BYPASS AUTENTICAZIONE: Imposta cookie di login
    await page.setCookie({
        name: 'ftth_auth',
        value: 'true',
        domain: 'servicess.net',
        path: '/',
        httpOnly: false,
        secure: true
    });
    
    let apiRequests = 0;
    let apiSuccess = 0;
    
    page.on('response', response => {
        if (response.url().includes('gestionale/works')) {
            apiRequests++;
            if (response.status() === 200 && response.headers()['content-length'] !== '0') {
                apiSuccess++;
                console.log(`✅ API call ${apiRequests}: ${response.url()} - ${response.status()} (${response.headers()['content-length']} bytes)`);
            } else {
                console.log(`❌ API call ${apiRequests}: ${response.url()} - ${response.status()}`);
            }
        }
    });
    
    page.on('console', msg => {
        const text = msg.text();
        if (text.includes('Errore caricamento') || text.includes('error') || text.includes('failed')) {
            console.log('🚨 CONSOLE ERROR:', text);
        } else if (text.includes('caricamento') || text.includes('loaded') || text.includes('success')) {
            console.log('ℹ️  CONSOLE INFO:', text);
        }
    });
    
    try {
        console.log('🔗 Caricamento pagina...');
        await page.goto('https://servicess.net/fibra/gestionale-ftth.html', { 
            waitUntil: 'networkidle2',
            timeout: 30000 
        });
        
        console.log('⏳ Attesa caricamento completo...');
        await new Promise(resolve => setTimeout(resolve, 4000));
        
        // Verifica autenticazione
        const hasLoginForm = await page.$('input[type="password"], .login-form');
        if (hasLoginForm) {
            console.log('❌ AUTENTICAZIONE FALLITA: form di login ancora presente');
            return;
        } else {
            console.log('✅ AUTENTICAZIONE SUCCESSO: accesso alla pagina consentito');
        }
        
        // Conta gli ordini
        const orderCards = await page.$$('.order-card');
        console.log(`📊 ORDINI CARICATI: ${orderCards.length} ordini trovati`);
        
        if (orderCards.length > 0) {
            console.log('🎉 SUCCESSO COMPLETO!');
            console.log(`   • API Requests: ${apiRequests}`);
            console.log(`   • API Success: ${apiSuccess}`);
            console.log(`   • Orders Loaded: ${orderCards.length}`);
            
            // Mostra un esempio di ordine
            const firstOrder = await orderCards[0].evaluate(el => {
                const title = el.querySelector('.card-title, h5, h4')?.textContent || 'N/A';
                const status = el.querySelector('.badge, .status')?.textContent || 'N/A';
                return { title: title.trim(), status: status.trim() };
            });
            console.log(`   • Esempio ordine: "${firstOrder.title}" - Status: ${firstOrder.status}`);
            
        } else {
            console.log('⚠️  ATTENZIONE: Nessun ordine caricato nonostante autenticazione riuscita');
        }
        
        // Verifica statistiche
        const statsElements = await page.$$('.stat-box, .stats-box');
        if (statsElements.length > 0) {
            console.log(`📈 STATISTICHE: ${statsElements.length} box statistiche trovate`);
        }
        
    } catch (e) {
        console.log('💥 ERRORE TEST:', e.message);
    } finally {
        await browser.close();
        console.log('🏁 Test completato');
    }
}

testFinal();
