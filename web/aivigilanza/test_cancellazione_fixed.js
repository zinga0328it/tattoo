const puppeteer = require('puppeteer');

async function testCancellazione() {
    console.log('Apertura pagina gestionale...');
    const browser = await puppeteer.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    
    // Abilita logging dettagliato
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    page.on('response', response => {
        if (response.url().includes('gestionale/works')) {
            console.log('API RESPONSE:', response.url(), response.status());
        }
    });
    
    try {
        await page.goto('https://servicess.net/fibra/gestionale-ftth.html', { 
            waitUntil: 'networkidle2',
            timeout: 30000 
        });
        
        // Aspetta che la funzione loadOrders sia disponibile
        await page.waitForFunction(() => typeof loadOrders === 'function', { timeout: 10000 });
        
        // Aspetta un po' per essere sicuri
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Controlla se ci sono errori nella console
        const errors = [];
        page.on('pageerror', error => {
            errors.push(error.message);
            console.log('PAGE ERROR:', error.message);
        });
        
        // Prova ad aspettare gli elementi order-card
        try {
            await page.waitForSelector('.order-card', { timeout: 15000 });
            console.log('SUCCESS: order-card elements found!');
            
            // Conta quanti elementi ci sono
            const count = await page.$$eval('.order-card', cards => cards.length);
            console.log(`Found ${count} order cards`);
            
        } catch (e) {
            console.log('ERROR: order-card elements not found within timeout');
            console.log('Checking if API was called...');
            
            // Controlla se ci sono stati errori nella funzione loadOrders
            const apiErrors = await page.evaluate(() => {
                // Prova a chiamare loadOrders manualmente e cattura errori
                return new Promise((resolve) => {
                    const originalError = console.error;
                    const errors = [];
                    console.error = (...args) => {
                        errors.push(args.join(' '));
                        originalError.apply(console, args);
                    };
                    
                    try {
                        loadOrders().then(() => {
                            setTimeout(() => resolve(errors), 2000);
                        }).catch(err => {
                            resolve(['loadOrders failed:', err.message]);
                        });
                    } catch (e) {
                        resolve(['loadOrders exception:', e.message]);
                    }
                });
            });
            
            console.log('API Errors:', apiErrors);
        }
        
    } catch (e) {
        console.log('Errore test:', e.message);
    } finally {
        await browser.close();
    }
}

testCancellazione();
