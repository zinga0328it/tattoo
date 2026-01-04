const puppeteer = require('puppeteer');

async function debugTest() {
    console.log('Debug test - apertura pagina...');
    const browser = await puppeteer.launch({ 
        headless: false,  // Modalità non headless per vedere cosa succede
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    
    // Cattura tutti i log
    page.on('console', msg => {
        console.log('CONSOLE:', msg.type(), msg.text());
    });
    
    page.on('response', response => {
        if (response.url().includes('gestionale')) {
            console.log('RESPONSE:', response.url(), response.status());
        }
    });
    
    page.on('requestfailed', request => {
        console.log('REQUEST FAILED:', request.url(), request.failure().errorText);
    });
    
    try {
        console.log('Navigating to page...');
        await page.goto('https://servicess.net/fibra/gestionale-ftth.html', { 
            waitUntil: 'domcontentloaded',
            timeout: 30000 
        });
        
        console.log('Page loaded, waiting for loadOrders...');
        
        // Aspetta che loadOrders sia definita
        await page.waitForFunction(() => typeof loadOrders !== 'undefined', { timeout: 10000 });
        
        console.log('Calling loadOrders manually...');
        
        // Chiama loadOrders e cattura eventuali errori
        const result = await page.evaluate(async () => {
            try {
                console.log('Inside evaluate: calling loadOrders');
                await loadOrders();
                console.log('loadOrders completed successfully');
                return { success: true };
            } catch (error) {
                console.error('Error in loadOrders:', error);
                return { success: false, error: error.message, stack: error.stack };
            }
        });
        
        console.log('Result:', result);
        
        // Aspetta un po' per vedere se appaiono elementi
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        const orderCards = await page.$$eval('.order-card', cards => cards.length);
        console.log('Order cards found:', orderCards);
        
    } catch (e) {
        console.log('Test error:', e.message);
    }
    
    // Non chiudere automaticamente per permettere all'utente di vedere
    console.log('Browser aperto - premi Ctrl+C per chiudere');
    // await browser.close();
}

debugTest();
