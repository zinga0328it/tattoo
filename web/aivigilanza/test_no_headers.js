const puppeteer = require('puppeteer');

async function testNoHeaders() {
    console.log('Test senza header identificativi...');
    const browser = await puppeteer.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    
    // Rimuovi tutti gli header che potrebbero identificare Puppeteer
    await page.setRequestInterception(true);
    
    page.on('request', request => {
        const headers = { ...request.headers() };
        
        // Rimuovi header specifici di Chrome/Puppeteer
        delete headers['sec-ch-ua'];
        delete headers['sec-ch-ua-mobile'];
        delete headers['sec-ch-ua-platform'];
        delete headers['sec-fetch-dest'];
        delete headers['sec-fetch-mode'];
        delete headers['sec-fetch-site'];
        delete headers['sec-fetch-user'];
        delete headers['upgrade-insecure-requests'];
        
        // Mantieni solo header essenziali
        const cleanHeaders = {
            'accept': headers.accept || '*/*',
            'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': headers.referer
        };
        
        // Aggiungi X-API-Key per le richieste API
        if (request.url().includes('/gestionale/')) {
            cleanHeaders['x-api-key'] = 'JHzxUzdAK8LJ33Y50MDgLf5E62flYset4MYA6ELpXpU=';
        }
        
        request.continue({ headers: cleanHeaders });
    });
    
    page.on('console', msg => {
        if (msg.text().includes('Errore') || msg.text().includes('error') || msg.text().includes('fetch')) {
            console.log('CONSOLE:', msg.text());
        }
    });
    
    page.on('response', response => {
        if (response.url().includes('gestionale/works')) {
            console.log('API RESPONSE:', response.url(), response.status(), 'Content-Length:', response.headers()['content-length']);
        }
    });
    
    try {
        await page.goto('https://servicess.net/fibra/gestionale-ftth.html', { 
            waitUntil: 'networkidle2',
            timeout: 30000 
        });
        
        // Aspetta che la pagina sia pronta
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Cerca elementi order-card
        const orderCards = await page.$$('.order-card');
        console.log('Order cards found:', orderCards.length);
        
        if (orderCards.length > 0) {
            console.log('SUCCESS: Orders loaded!');
        } else {
            console.log('No order cards found');
        }
        
    } catch (e) {
        console.log('Test error:', e.message);
    } finally {
        await browser.close();
    }
}

testNoHeaders();
