
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

const FRAME_DIR = '/tmp/demo-frames-narrated';
const FPS = 4;
const TOTAL_DURATION = 85.752;
const SCENES = [{"action": "dashboard", "start": 0, "duration": 5.808}, {"action": "dashboard", "start": 6.608, "duration": 11.52}, {"action": "scroll_down", "start": 18.928, "duration": 10.752}, {"action": "predict_0", "start": 30.480000000000004, "duration": 7.08}, {"action": "simulate_0", "start": 38.36000000000001, "duration": 15.312}, {"action": "predict_2", "start": 54.47200000000001, "duration": 9.384}, {"action": "predict_4", "start": 64.656, "duration": 14.472}, {"action": "scroll_up", "start": 79.92800000000001, "duration": 5.76}];

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
    
    // Check if we need to trigger a new scene action
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
        } else if (action === 'api_page') {
          await page.goto('http://localhost:8000/', { waitUntil: 'networkidle0' });
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
