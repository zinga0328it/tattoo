const puppeteer = require('puppeteer');

async function testDirect() {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    
    // Abilita logging dettagliato
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    page.on('response', response => {
        console.log('RESPONSE:', response.url(), response.status());
        if (response.status() === 404) {
            console.log('404 URL:', response.url());
        }
    });
    
    await page.goto('https://servicess.net/fibra/gestionale-ftth.html');
    
    // Aspetta che la pagina si carichi
    await page.waitForTimeout(2000);
    
    // Prova una richiesta diretta
    const result = await page.evaluate(async () => {
        try {
            console.log('Testing direct fetch...');
            const response = await fetch('https://servicess.net/gestionale/works/', {
                headers: {
                    'X-API-Key': 'JHzxUzdAK8LJ33Y50MDgLf5E62flYset4MYA6ELpXpU='
                }
            });
            console.log('Status:', response.status);
            if (response.ok) {
                const data = await response.json();
                return { success: true, count: data.length };
            } else {
                return { success: false, status: response.status };
            }
        } catch (e) {
            console.log('Error:', e.message);
            return { success: false, error: e.message };
        }
    });
    
    console.log('Result:', result);
    await browser.close();
}

testDirect().catch(console.error);
