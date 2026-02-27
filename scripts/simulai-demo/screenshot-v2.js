const puppeteer = require('puppeteer-core');
(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/chromium',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
    headless: 'new'
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  const ws = '/home/node/.openclaw/workspace/';

  // Dashboard
  await page.goto('http://localhost:8000/dashboard', { waitUntil: 'networkidle0' });
  await page.screenshot({ path: ws + 'v2-dashboard.png', fullPage: true });
  console.log('1. Dashboard');

  // Twin detail - pump
  await page.goto('http://localhost:8000/twin/pump-001', { waitUntil: 'networkidle0' });
  await page.screenshot({ path: ws + 'v2-twin-detail.png', fullPage: true });
  console.log('2. Twin Detail (Pump)');

  // Alerts
  await page.goto('http://localhost:8000/alerts', { waitUntil: 'networkidle0' });
  await page.screenshot({ path: ws + 'v2-alerts.png', fullPage: true });
  console.log('3. Alerts');

  // Simulation Lab
  await page.goto('http://localhost:8000/simulation', { waitUntil: 'networkidle0' });
  await page.screenshot({ path: ws + 'v2-simulation.png', fullPage: true });
  console.log('4. Simulation Lab');

  // Analytics
  await page.goto('http://localhost:8000/analytics', { waitUntil: 'networkidle0' });
  await page.screenshot({ path: ws + 'v2-analytics.png', fullPage: true });
  console.log('5. Analytics');

  await browser.close();
  console.log('Done');
})();
