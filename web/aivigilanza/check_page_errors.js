const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({headless:true,args:['--no-sandbox','--disable-setuid-sandbox']});
  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
  await page.setCookie({name:'ftth_auth', value:'true', domain:'servicess.net', path:'/', secure:true, sameSite:'None'});

  page.on('pageerror', err => console.log('PAGE ERROR:', err.message));
  page.on('console', msg => console.log('CONSOLE:', msg.text()));

  await page.goto('https://servicess.net/fibra/gestionale-ftth.html', {waitUntil:'networkidle2', timeout:30000});
  await new Promise(r => setTimeout(r, 5000));
  await browser.close();
})();
