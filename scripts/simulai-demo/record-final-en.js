
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const FRAME_DIR = '/tmp/final-frames-en';
const FPS = 6;
const TOTAL = 90.796;
const SCENES = [{"start": 0.3, "duration": 6.768, "action": "dashboard_hold"}, {"start": 7.667999999999999, "duration": 11.232, "action": "dashboard_scroll"}, {"start": 19.5, "duration": 8.832, "action": "twin_pump"}, {"start": 28.932000000000002, "duration": 8.4, "action": "twin_pump_scroll"}, {"start": 37.932, "duration": 7.32, "action": "twin_cnc"}, {"start": 45.852000000000004, "duration": 9.672, "action": "alerts"}, {"start": 56.124, "duration": 7.536, "action": "sim_config"}, {"start": 64.26, "duration": 8.544, "action": "sim_run"}, {"start": 73.40400000000001, "duration": 9.816, "action": "analytics"}, {"start": 83.82000000000001, "duration": 5.376, "action": "dashboard_finale"}];

(async () => {
  if (fs.existsSync(FRAME_DIR)) execSync('rm -rf ' + FRAME_DIR);
  fs.mkdirSync(FRAME_DIR, { recursive: true });

  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/chromium',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
    headless: 'new'
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  await page.goto('http://localhost:8000/dashboard', { waitUntil: 'networkidle0' });

  let frame = 0;
  let triggered = new Set();
  const totalFrames = Math.ceil(TOTAL * FPS);

  for (let f = 0; f < totalFrames; f++) {
    const t = f / FPS;

    for (let s = 0; s < SCENES.length; s++) {
      if (!triggered.has(s) && t >= SCENES[s].start && t < SCENES[s].start + 0.5) {
        triggered.add(s);
        const a = SCENES[s].action;
        console.log('  ' + t.toFixed(1) + 's: ' + a);

        try {
          if (a === 'dashboard_hold') {
            // already there
          } else if (a === 'dashboard_scroll') {
            await page.evaluate(() => window.scrollTo({ top: 400, behavior: 'smooth' }));
          } else if (a === 'twin_pump') {
            await page.goto('http://localhost:8000/twin/pump-001', { waitUntil: 'networkidle0' });
          } else if (a === 'twin_pump_scroll') {
            await page.evaluate(() => window.scrollTo({ top: 500, behavior: 'smooth' }));
          } else if (a === 'twin_cnc') {
            await page.goto('http://localhost:8000/twin/cnc-lathe-001', { waitUntil: 'networkidle0' });
          } else if (a === 'alerts') {
            await page.goto('http://localhost:8000/alerts', { waitUntil: 'networkidle0' });
          } else if (a === 'sim_config') {
            await page.goto('http://localhost:8000/simulation', { waitUntil: 'networkidle0' });
          } else if (a === 'sim_run') {
            const btn = await page.$('#sim-btn');
            if (btn) await btn.click();
          } else if (a === 'analytics') {
            await page.goto('http://localhost:8000/analytics', { waitUntil: 'networkidle0' });
            await new Promise(r => setTimeout(r, 500));
            await page.evaluate(() => window.scrollTo({ top: 300, behavior: 'smooth' }));
          } else if (a === 'dashboard_finale') {
            await page.goto('http://localhost:8000/dashboard', { waitUntil: 'networkidle0' });
          }
        } catch(e) { console.log('    error: ' + e.message); }
        await new Promise(r => setTimeout(r, 150));
      }
    }

    const fname = path.join(FRAME_DIR, 'frame_' + String(f).padStart(5, '0') + '.png');
    await page.screenshot({ path: fname });
    frame++;
  }

  await browser.close();
  console.log('Captured ' + frame + ' frames (' + (frame/FPS).toFixed(1) + 's)');
})();
