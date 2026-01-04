const puppeteer = require('puppeteer');

async function testDirectAPI() {
    console.log('Test con API diretta al backend Yggdrasil...');
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
        if (response.url().includes('works')) {
            console.log('API RESPONSE:', response.url(), response.status(), 'Content-Length:', response.headers()['content-length']);
        }
    });
    
    try {
        await page.goto('https://servicess.net/fibra/gestionale-ftth.html', { 
            waitUntil: 'networkidle2',
            timeout: 30000 
        });
        
        // Inietta JavaScript per modificare apiFetch e puntare direttamente al backend
        await page.evaluate(() => {
            // Override della funzione apiFetch per bypassare il proxy
            window.originalApiFetch = window.apiFetch;
            
            window.apiFetch = function(path, opts = {}) {
                // Usa direttamente l'IPv6 del backend invece del proxy
                const directUrl = 'http://[200:421e:6385:4a8b:dca7:cfb:197f:e9c3]:6030' + path;
                
                if (!opts.headers) opts.headers = {};
                opts.headers['X-API-Key'] = 'JHzxUzdAK8LJ33Y50MDgLf5E62flYset4MYA6ELpXpU=';
                
                console.log('Direct API call to:', directUrl);
                return fetch(directUrl, opts);
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
            console.log('SUCCESS: Orders loaded via direct API!');
            
            // Mostra alcuni dettagli del primo ordine
            const firstCard = orderCards[0];
            const text = await firstCard.evaluate(el => el.textContent);
            console.log('First order preview:', text.substring(0, 100) + '...');
        } else {
            console.log('No order cards found');
        }
        
    } catch (e) {
        console.log('Test error:', e.message);
    } finally {
        await browser.close();
    }
}

testDirectAPI();
