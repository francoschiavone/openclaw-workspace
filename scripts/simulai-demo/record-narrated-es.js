
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

const FRAME_DIR = '/tmp/demo-frames-narrated';
const FPS = 4;
const TOTAL_DURATION = 99.83200000000001;
const SCENES = [{"action": "dashboard", "start": 0, "duration": 6.312}, {"action": "dashboard", "start": 7.112, "duration": 13.032}, {"action": "scroll_down", "start": 20.944000000000003, "duration": 12.168}, {"action": "predict_0", "start": 33.912000000000006, "duration": 9.528}, {"action": "simulate_0", "start": 44.24000000000001, "duration": 17.664}, {"action": "predict_2", "start": 62.70400000000001, "duration": 10.776}, {"action": "predict_4", "start": 74.28, "duration": 17.832}, {"action": "scroll_up", "start": 92.912, "duration": 6.12}];

(async () => {
  if (fs.existsSync(FRAME_DIR)) require('child_process').execSync('rm -rf ' + FRAME_DIR);
  fs.mkdirSync(FRAME_DIR, { recursive: true });

  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/chromium',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
    headless: 'new'
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 900 });
  await page.goto('http://localhost:8000/dashboard', { waitUntil: 'networkidle0' });

  let frame = 0;
  let currentScene = -1;
  const totalFrames = Math.ceil(TOTAL_DURATION * FPS);

  for (let f = 0; f < totalFrames; f++) {
    const currentTime = f / FPS;
    for (let s = 0; s < SCENES.length; s++) {
      if (s > currentScene && currentTime >= SCENES[s].start && currentTime < SCENES[s].start + 0.3) {
        currentScene = s;
        const action = SCENES[s].action;
        console.log('Scene ' + s + ': ' + action + ' at ' + currentTime.toFixed(1) + 's');
        if (action === 'scroll_down') {
          await page.evaluate(() => window.scrollTo({ top: 500, behavior: 'smooth' }));
        } else if (action === 'scroll_up') {
          await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
        } else if (action.startsWith('predict_')) {
          const idx = parseInt(action.split('_')[1]);
          const btns = await page.$$('.btn-predict');
          if (btns[idx]) await btns[idx].click();
        } else if (action.startsWith('simulate_')) {
          const idx = parseInt(action.split('_')[1]);
          const btns = await page.$$('.btn-simulate');
          if (btns[idx]) await btns[idx].click();
        }
        await new Promise(r => setTimeout(r, 200));
      }
    }
    const fname = path.join(FRAME_DIR, 'frame_' + String(f).padStart(5, '0') + '.png');
    await page.screenshot({ path: fname });
    frame++;
  }
  await browser.close();
  console.log('Captured ' + frame + ' frames over ' + TOTAL_DURATION.toFixed(1) + 's');
})();
