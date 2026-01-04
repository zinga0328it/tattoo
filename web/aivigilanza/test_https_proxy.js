const puppeteer = require('puppeteer');

async function testHttpsProxy() {
    console.log('Test con proxy HTTPS che converte a HTTP...');
    const browser = await puppeteer.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    
    // User agent normale
    await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
    
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
        
        // Inietta JavaScript per modificare apiFetch e usare HTTPS proxy
        await page.evaluate(() => {
            // Override della funzione apiFetch per usare HTTPS proxy
            window.originalApiFetch = window.apiFetch;
            
            window.apiFetch = function(path, opts = {}) {
                // Usa il proxy HTTPS che Apache converte in HTTP
                const proxyUrl = 'https://servicess.net/gestionale' + path;
                
                if (!opts.headers) opts.headers = {};
                opts.headers['X-API-Key'] = 'JHzxUzdAK8LJ33Y50MDgLf5E62flYset4MYA6ELpXpU=';
                
                console.log('Proxy API call to:', proxyUrl);
                return fetch(proxyUrl, opts);
            };
        });
        
        // Aspetta un po' e ricarica gli ordini
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Chiama manualmente loadOrders
        await page.evaluate(() => {
            if (window.loadOrders) {
                window.loadOrders();
            }
        });
        
        // Aspetta che gli ordini si carichino
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Cerca elementi order-card
        const orderCards = await page.$$('.order-card');
        console.log('Order cards found:', orderCards.length);
        
        if (orderCards.length > 0) {
            console.log('SUCCESS: Orders loaded via HTTPS proxy!');
        } else {
            console.log('No order cards found - checking page content...');
            
            // Debug: mostra il contenuto della pagina
            const bodyText = await page.evaluate(() => document.body.innerText);
            console.log('Page contains:', bodyText.substring(0, 200) + '...');
        }
        
    } catch (e) {
        console.log('Test error:', e.message);
    } finally {
        await browser.close();
    }
}

testHttpsProxy();
