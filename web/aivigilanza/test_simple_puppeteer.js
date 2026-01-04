const puppeteer = require('puppeteer');

async function testSimple() {
    console.log('Testing simple page...');
    const browser = await puppeteer.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    page.on('response', response => {
        if (response.url().includes('gestionale')) {
            console.log('API RESPONSE:', response.url(), response.status());
        }
    });
    
    try {
        await page.goto('https://servicess.net/fibra/test-simple.html', { 
            waitUntil: 'networkidle2',
            timeout: 30000 
        });
        
        // Aspetta che il test finisca
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Controlla il contenuto della pagina
        const content = await page.$eval('#ordersList', el => el.textContent);
        console.log('Page content:', content);
        
    } catch (e) {
        console.log('Error:', e.message);
    } finally {
        await browser.close();
    }
}

testSimple();
