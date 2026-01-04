const puppeteer = require('puppeteer');

async function testIntercept() {
    console.log('Test con intercettazione richieste...');
    const browser = await puppeteer.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    
    // Intercetta tutte le richieste
    await page.setRequestInterception(true);
    
    page.on('request', request => {
        const url = request.url();
        if (url.includes('gestionale/works')) {
            console.log('INTERCEPTED REQUEST:', request.method(), url);
            console.log('HEADERS:', JSON.stringify(request.headers(), null, 2));
            
            // Continua la richiesta normalmente
            request.continue();
        } else {
            request.continue();
        }
    });
    
    page.on('response', response => {
        const url = response.url();
        if (url.includes('gestionale/works')) {
            console.log('RESPONSE STATUS:', response.status(), url);
            if (response.status() !== 200) {
                console.log('RESPONSE HEADERS:', JSON.stringify(response.headers(), null, 2));
            }
        }
    });
    
    page.on('console', msg => {
        if (msg.text().includes('Errore') || msg.text().includes('error') || msg.text().includes('fetch')) {
            console.log('CONSOLE:', msg.text());
        }
    });
    
    try {
        await page.goto('https://servicess.net/fibra/gestionale-ftth.html', { 
            waitUntil: 'networkidle2',
            timeout: 30000 
        });
        
        // Aspetta un po'
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        console.log('Test completato');
        
    } catch (e) {
        console.log('Test error:', e.message);
    } finally {
        await browser.close();
    }
}

testIntercept();
