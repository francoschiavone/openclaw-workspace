const puppeteer = require('puppeteer-core');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const FRAME_DIR = '/tmp/demo-frames-v2';
const FPS = 6;

(async () => {
  if (fs.existsSync(FRAME_DIR)) execSync(`rm -rf ${FRAME_DIR}`);
  fs.mkdirSync(FRAME_DIR, { recursive: true });

  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/chromium',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
    headless: 'new'
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  let frame = 0;
  async function capture(n = 1) {
    for (let i = 0; i < n; i++) {
      await page.screenshot({ path: path.join(FRAME_DIR, `frame_${String(frame).padStart(5, '0')}.png`) });
      frame++;
    }
  }
  async function hold(seconds) { await capture(Math.ceil(seconds * FPS)); }
  async function smooth(ms) { await new Promise(r => setTimeout(r, ms)); await capture(); }

  // --- SCENE 1: Dashboard ---
  console.log('Scene 1: Dashboard overview');
  await page.goto('http://localhost:8000/dashboard', { waitUntil: 'networkidle0' });
  await hold(4);

  // Scroll to see all twins
  console.log('Scene 2: Scroll dashboard');
  for (let y = 0; y <= 400; y += 40) {
    await page.evaluate((y) => window.scrollTo(0, y), y);
    await smooth(80);
  }
  await hold(3);

  // Scroll back up
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  await hold(1.5);

  // --- SCENE 3: Click into Coolant Pump (critical) ---
  console.log('Scene 3: Coolant Pump detail');
  await page.goto('http://localhost:8000/twin/pump-001', { waitUntil: 'networkidle0' });
  await hold(4);
  
  // Scroll to see prediction
  for (let y = 0; y <= 500; y += 50) {
    await page.evaluate((y) => window.scrollTo(0, y), y);
    await smooth(80);
  }
  await hold(3);

  // --- SCENE 4: CNC Lathe detail ---
  console.log('Scene 4: CNC Lathe detail');
  await page.goto('http://localhost:8000/twin/cnc-lathe-001', { waitUntil: 'networkidle0' });
  await hold(3);
  for (let y = 0; y <= 400; y += 50) {
    await page.evaluate((y) => window.scrollTo(0, y), y);
    await smooth(80);
  }
  await hold(2);

  // --- SCENE 5: Alerts page ---
  console.log('Scene 5: Alerts');
  await page.goto('http://localhost:8000/alerts', { waitUntil: 'networkidle0' });
  await hold(4);
  
  // Scroll alerts
  for (let y = 0; y <= 300; y += 50) {
    await page.evaluate((y) => window.scrollTo(0, y), y);
    await smooth(80);
  }
  await hold(2);

  // --- SCENE 6: Simulation Lab ---
  console.log('Scene 6: Simulation Lab');
  await page.goto('http://localhost:8000/simulation', { waitUntil: 'networkidle0' });
  await hold(3);

  // Adjust slider
  console.log('  Adjusting slider...');
  const slider = await page.$('#sim-range');
  if (slider) {
    const box = await slider.boundingBox();
    // Move slider to +40
    await page.mouse.click(box.x + box.width * 0.7, box.y + box.height / 2);
    await hold(1);
  }

  // Click Run Simulation
  console.log('  Running simulation...');
  const runBtn = await page.$('#sim-btn');
  if (runBtn) {
    await runBtn.click();
    await hold(2.5); // Loading state
    await hold(4);   // Results
  }

  // Scroll to see history table
  for (let y = 0; y <= 400; y += 50) {
    await page.evaluate((y) => window.scrollTo(0, y), y);
    await smooth(80);
  }
  await hold(3);

  // --- SCENE 7: Analytics ---
  console.log('Scene 7: Analytics');
  await page.goto('http://localhost:8000/analytics', { waitUntil: 'networkidle0' });
  await hold(4);

  // Scroll through analytics
  for (let y = 0; y <= 600; y += 40) {
    await page.evaluate((y) => window.scrollTo(0, y), y);
    await smooth(80);
  }
  await hold(4);

  // --- SCENE 8: Back to dashboard for finale ---
  console.log('Scene 8: Dashboard finale');
  await page.goto('http://localhost:8000/dashboard', { waitUntil: 'networkidle0' });
  await hold(3);

  await browser.close();
  
  const totalSec = (frame / FPS).toFixed(1);
  console.log(`\nCaptured ${frame} frames (${totalSec}s at ${FPS}fps)`);

  // Encode video
  console.log('Encoding video...');
  execSync(`ffmpeg -y -framerate ${FPS} -i ${FRAME_DIR}/frame_%05d.png -c:v libx264 -pix_fmt yuv420p -vf "scale=1440:900" /home/node/.openclaw/workspace/simulai-demo-v2-silent.mp4 2>&1`);
  console.log('Silent video encoded');
})();
