const puppeteer = require('puppeteer');

async function testUserAgent() {
    console.log('Test con user agent personalizzato...');
    const browser = await puppeteer.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    
    // User agent che non contiene "Headless"
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
        
        // Aspetta che la pagina sia pronta
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Cerca elementi order-card
        const orderCards = await page.$$('.order-card');
        console.log('Order cards found:', orderCards.length);
        
        if (orderCards.length > 0) {
            console.log('SUCCESS: Orders loaded!');
            
            // Mostra alcuni dettagli del primo ordine
            const firstCard = orderCards[0];
            const text = await firstCard.evaluate(el => el.textContent);
            console.log('First order preview:', text.substring(0, 100) + '...');
        } else {
            console.log('No order cards found - checking for errors...');
            
            // Controlla se ci sono messaggi di errore nella pagina
            const errorMessages = await page.$$eval('.notification, .alert, [style*="color:red"], [style*="background:red"]', 
                elements => elements.map(el => el.textContent));
            console.log('Error messages found:', errorMessages);
        }
        
    } catch (e) {
        console.log('Test error:', e.message);
    } finally {
        await browser.close();
    }
}

testUserAgent();
