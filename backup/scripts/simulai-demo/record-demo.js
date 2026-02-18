const puppeteer = require('puppeteer-core');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const FRAME_DIR = '/tmp/demo-frames';
const OUTPUT = '/home/node/.openclaw/workspace/simulai-demo.mp4';
const FPS = 4; // 4 frames per second for smooth-ish video
const FRAME_DELAY = 250; // ms between frames

(async () => {
  // Clean frame dir
  if (fs.existsSync(FRAME_DIR)) execSync(`rm -rf ${FRAME_DIR}`);
  fs.mkdirSync(FRAME_DIR, { recursive: true });

  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/chromium',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
    headless: 'new'
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 900 });

  let frame = 0;
  async function capture() {
    const fname = path.join(FRAME_DIR, `frame_${String(frame).padStart(5, '0')}.png`);
    await page.screenshot({ path: fname });
    frame++;
  }
  async function wait(ms) {
    const frames = Math.ceil(ms / FRAME_DELAY);
    for (let i = 0; i < frames; i++) {
      await capture();
      await new Promise(r => setTimeout(r, 50));
    }
  }

  // Scene 1: Open dashboard (3 seconds)
  console.log('Scene 1: Dashboard overview');
  await page.goto('http://localhost:8000/dashboard', { waitUntil: 'networkidle0' });
  await wait(3000);

  // Scene 2: Scroll down to see Coolant Pump (2 seconds)
  console.log('Scene 2: Scroll to see all twins');
  await page.evaluate(() => window.scrollTo({ top: 300, behavior: 'smooth' }));
  await wait(2000);

  // Scene 3: Scroll back up (1 second)
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  await wait(1500);

  // Scene 4: Click Predict on CNC Lathe (3 seconds)
  console.log('Scene 3: Predict CNC Lathe');
  const predictBtns = await page.$$('.btn-predict');
  if (predictBtns.length >= 1) {
    await predictBtns[0].click();
    await wait(3000);
  }

  // Scene 5: Click Simulate on CNC Lathe (3 seconds)
  console.log('Scene 4: Simulate CNC Lathe');
  const simBtns = await page.$$('.btn-simulate');
  if (simBtns.length >= 1) {
    await simBtns[0].click();
    await wait(3000);
  }

  // Scene 6: Click Predict on Robotic Arm (2 seconds)
  console.log('Scene 5: Predict Robotic Arm');
  if (predictBtns.length >= 2) {
    await predictBtns[1].click();
    await wait(2500);
  }

  // Scene 7: Click Predict on HVAC (warning) (3 seconds)
  console.log('Scene 6: Predict HVAC (warning)');
  if (predictBtns.length >= 3) {
    await predictBtns[2].click();
    await wait(3000);
  }

  // Scene 8: Scroll down to Coolant Pump (degraded) (2 seconds)
  console.log('Scene 7: Scroll to Coolant Pump');
  await page.evaluate(() => window.scrollTo({ top: 600, behavior: 'smooth' }));
  await wait(2000);

  // Scene 9: Click Predict on Coolant Pump - the critical one (4 seconds)
  console.log('Scene 8: Predict Coolant Pump (HIGH RISK)');
  if (predictBtns.length >= 5) {
    await predictBtns[4].click();
    await wait(4000);
  }

  // Scene 10: Click Simulate on Coolant Pump (3 seconds)
  console.log('Scene 9: Simulate Coolant Pump');
  if (simBtns.length >= 5) {
    await simBtns[4].click();
    await wait(3000);
  }

  // Scene 11: Scroll to see full results (2 seconds)
  await page.evaluate(() => window.scrollTo({ top: 900, behavior: 'smooth' }));
  await wait(2500);

  // Scene 12: Back to top for finale (2 seconds)
  console.log('Scene 10: Finale');
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  await wait(2000);

  // Scene 13: Visit API page (3 seconds)
  console.log('Scene 11: API endpoints');
  await page.goto('http://localhost:8000/', { waitUntil: 'networkidle0' });
  await wait(3000);

  await browser.close();
  console.log(`Captured ${frame} frames`);

  // Encode to MP4 with ffmpeg
  console.log('Encoding video...');
  execSync(`ffmpeg -y -framerate ${FPS} -i ${FRAME_DIR}/frame_%05d.png -c:v libx264 -pix_fmt yuv420p -vf "scale=1400:900" ${OUTPUT} 2>&1`);
  
  const stats = fs.statSync(OUTPUT);
  console.log(`Video saved: ${OUTPUT} (${(stats.size / 1024 / 1024).toFixed(1)}MB)`);
})();
