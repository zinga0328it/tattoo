const puppeteer = require('puppeteer');

async function testWithHeaders() {
    console.log('Test con header specifici...');
    const browser = await puppeteer.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    
    // Imposta user agent normale
    await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
    
    // Rimuovi header che potrebbero identificare Puppeteer
    await page.setExtraHTTPHeaders({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Linux"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1'
    });
    
    page.on('console', msg => {
        if (msg.text().includes('Errore') || msg.text().includes('error')) {
            console.log('CONSOLE ERROR:', msg.text());
        }
    });
    
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
        
        // Aspetta che la pagina sia pronta
        await page.waitForTimeout(3000);
        
        // Cerca elementi order-card
        const orderCards = await page.$$('.order-card');
        console.log('Order cards found:', orderCards.length);
        
        if (orderCards.length > 0) {
            console.log('SUCCESS: Orders loaded!');
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

testWithHeaders();
