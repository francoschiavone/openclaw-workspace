const puppeteer = require('puppeteer-core');

(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/chromium',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
    headless: 'new'
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 900 });
  
  // Dashboard
  await page.goto('http://localhost:8000/dashboard', { waitUntil: 'networkidle0' });
  await page.screenshot({ path: 'demo-dashboard.png', fullPage: true });
  console.log('Dashboard captured');
  
  // Click predict on pump-001 (the degraded one - 5th card)
  const predictBtns = await page.$$('.btn-predict');
  if (predictBtns.length >= 5) {
    await predictBtns[4].click();
    await new Promise(r => setTimeout(r, 1500));
  }
  // Click simulate on CNC (1st card)
  const simBtns = await page.$$('.btn-simulate');
  if (simBtns.length >= 1) {
    await simBtns[0].click();
    await new Promise(r => setTimeout(r, 1500));
  }
  // Click predict on HVAC too (3rd card)
  if (predictBtns.length >= 3) {
    await predictBtns[2].click();
    await new Promise(r => setTimeout(r, 1500));
  }
  await page.screenshot({ path: 'demo-dashboard-ai.png', fullPage: true });
  console.log('Dashboard with AI results captured');
  
  // API root page
  await page.goto('http://localhost:8000/', { waitUntil: 'networkidle0' });
  await page.screenshot({ path: 'demo-api.png' });
  console.log('API page captured');
  
  await browser.close();
  console.log('Done!');
})();
