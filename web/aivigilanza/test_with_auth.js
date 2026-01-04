const puppeteer = require('puppeteer');

async function testWithAuth() {
    console.log('Test con autenticazione bypassata...');
    const browser = await puppeteer.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    
    // User agent normale
    await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
    
    // Imposta il cookie di autenticazione prima di caricare la pagina
    await page.setCookie({
        name: 'ftth_auth',
        value: 'true',
        domain: 'servicess.net',
        path: '/',
        httpOnly: false,
        secure: true
    });
    
    page.on('console', msg => {
        if (msg.text().includes('Errore') || msg.text().includes('error') || msg.text().includes('fetch') || msg.text().includes('caricamento')) {
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
        
        // Aspetta che la pagina si carichi completamente
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Cerca elementi order-card
        const orderCards = await page.$$('.order-card');
        console.log('Order cards found:', orderCards.length);
        
        if (orderCards.length > 0) {
            console.log('SUCCESS: Orders loaded with authentication!');
            
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
            
            // Debug: controlla se la pagina contiene ancora il form di login
            const hasLoginForm = await page.$('input[type="password"], .login-form, #password-input');
            if (hasLoginForm) {
                console.log('Login form still present - authentication failed');
            } else {
                console.log('No login form - authentication successful but no orders loaded');
            }
        }
        
    } catch (e) {
        console.log('Test error:', e.message);
    } finally {
        await browser.close();
    }
}

testWithAuth();
