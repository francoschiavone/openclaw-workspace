"""
Generate narrated SimulAI demo - sequential narration, no overlap
Records video scenes timed to match narration duration
"""
import sys
sys.path.insert(0, '/home/node/.openclaw/workspace/pylibs')

import asyncio
import edge_tts
import subprocess
import os
import json

WORKSPACE = '/home/node/.openclaw/workspace'

# Each scene: (narration_text, puppeteer_action)
# Actions: "dashboard", "scroll_down", "scroll_up", "predict_N", "simulate_N", "api_page"
SCENES_EN = [
    ("SimulAI. A Digital Twins platform powered by Artificial Intelligence.", "dashboard"),
    ("This is the main dashboard. Five digital twins monitoring industrial equipment in real time. Each twin shows health status, live sensors, and operational state.", "dashboard"),
    ("The coolant pump is in critical condition. Only 43 percent health. Temperature at 89 degrees, vibration way above threshold.", "scroll_down"),
    ("Let's use the AI to predict failures on the CNC lathe. Low risk. The machine is running well.", "predict_0"),
    ("Now, a what-if simulation. What happens if we increase RPM by 40 percent? Energy consumption jumps 53 percent. Mechanical wear increases 85 percent. The AI recommends caution.", "simulate_0"),
    ("The HVAC unit shows medium risk. Estimated failure in about two weeks. Gradual filter degradation is the root cause.", "predict_2"),
    ("Now the critical one. The coolant pump. High risk. Failure predicted within days. Overheating and excessive vibration detected. Seventy thousand dollars in maintenance costs can be avoided with immediate action.", "predict_4"),
    ("SimulAI. Make industrial decisions with certainty, not intuition.", "scroll_up"),
]

SCENES_ES = [
    ("SimulAI. Plataforma de gemelos digitales con inteligencia artificial.", "dashboard"),
    ("Este es el dashboard principal. Cinco gemelos digitales monitoreando equipos industriales en tiempo real. Cada twin muestra salud, sensores activos y estado operativo.", "dashboard"),
    ("La bomba de refrigerante está en estado crítico. Solo 43 por ciento de salud. Temperatura a 89 grados, vibración muy por encima del umbral.", "scroll_down"),
    ("Usamos la inteligencia artificial para predecir fallas en el torno CNC. Riesgo bajo. La máquina funciona bien.", "predict_0"),
    ("Ahora, una simulación. Qué pasa si subimos las RPM un 40 por ciento? El consumo energético sube 53 por ciento. El desgaste mecánico sube 85 por ciento. La IA recomienda precaución.", "simulate_0"),
    ("La unidad de climatización tiene riesgo medio. Falla estimada en unas dos semanas. Causa raíz: degradación gradual del filtro.", "predict_2"),
    ("Ahora el caso crítico. La bomba de refrigerante. Riesgo alto. Falla predicha en días. Sobretemperatura y vibración excesiva. Setenta mil dólares en costos de mantenimiento que se pueden evitar actuando ahora.", "predict_4"),
    ("SimulAI. Decisiones industriales con certeza, no con intuición.", "scroll_up"),
]

async def generate_segments(scenes, voice, output_dir, lang, rate="-5%"):
    os.makedirs(output_dir, exist_ok=True)
    durations = []
    for i, (text, action) in enumerate(scenes):
        output_file = os.path.join(output_dir, f"seg_{i:02d}.mp3")
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(output_file)
        # Get duration
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', output_file],
            capture_output=True, text=True
        )
        dur = float(result.stdout.strip())
        durations.append(dur)
        print(f"  [{lang}] {i}: {dur:.1f}s - {text[:60]}...")
    return durations

def concat_audio_with_pauses(segments_dir, durations, output_path, pause=0.8):
    """Concatenate segments with pauses, return total duration"""
    # Create silence file
    subprocess.run([
        'ffmpeg', '-y', '-f', 'lavfi', '-i', f'anullsrc=r=24000:cl=mono',
        '-t', str(pause), '-c:a', 'libmp3lame', '/tmp/silence.mp3'
    ], capture_output=True)
    
    # Build concat file
    with open('/tmp/concat.txt', 'w') as f:
        for i in range(len(durations)):
            seg_file = os.path.join(segments_dir, f"seg_{i:02d}.mp3")
            f.write(f"file '{seg_file}'\n")
            if i < len(durations) - 1:
                f.write(f"file '/tmp/silence.mp3'\n")
    
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', '/tmp/concat.txt',
        '-c:a', 'libmp3lame', '-b:a', '192k', output_path
    ], capture_output=True)
    
    # Get total duration
    result = subprocess.run(
        ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', output_path],
        capture_output=True, text=True
    )
    total = float(result.stdout.strip())
    
    # Calculate scene timestamps
    timestamps = []
    t = 0
    for i, dur in enumerate(durations):
        timestamps.append(t)
        t += dur + pause
    
    return total, timestamps

def generate_puppeteer_script(scenes, timestamps, durations, total_duration, output_video, fps=4):
    """Generate puppeteer script that records frames timed to narration"""
    scene_data = []
    for i, ((text, action), ts, dur) in enumerate(zip(scenes, timestamps, durations)):
        scene_data.append({"action": action, "start": ts, "duration": dur})
    
    script = f"""
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

const FRAME_DIR = '/tmp/demo-frames-narrated';
const FPS = {fps};
const TOTAL_DURATION = {total_duration};
const SCENES = {json.dumps(scene_data)};

(async () => {{
  if (fs.existsSync(FRAME_DIR)) require('child_process').execSync('rm -rf ' + FRAME_DIR);
  fs.mkdirSync(FRAME_DIR, {{ recursive: true }});

  const browser = await puppeteer.launch({{
    executablePath: '/usr/bin/chromium',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
    headless: 'new'
  }});
  const page = await browser.newPage();
  await page.setViewport({{ width: 1400, height: 900 }});
  await page.goto('http://localhost:8000/dashboard', {{ waitUntil: 'networkidle0' }});

  let frame = 0;
  let currentScene = -1;
  const totalFrames = Math.ceil(TOTAL_DURATION * FPS);

  for (let f = 0; f < totalFrames; f++) {{
    const currentTime = f / FPS;
    
    // Check if we need to trigger a new scene action
    for (let s = 0; s < SCENES.length; s++) {{
      if (s > currentScene && currentTime >= SCENES[s].start && currentTime < SCENES[s].start + 0.3) {{
        currentScene = s;
        const action = SCENES[s].action;
        console.log('Scene ' + s + ': ' + action + ' at ' + currentTime.toFixed(1) + 's');
        
        if (action === 'scroll_down') {{
          await page.evaluate(() => window.scrollTo({{ top: 500, behavior: 'smooth' }}));
        }} else if (action === 'scroll_up') {{
          await page.evaluate(() => window.scrollTo({{ top: 0, behavior: 'smooth' }}));
        }} else if (action.startsWith('predict_')) {{
          const idx = parseInt(action.split('_')[1]);
          const btns = await page.$$('.btn-predict');
          if (btns[idx]) await btns[idx].click();
        }} else if (action.startsWith('simulate_')) {{
          const idx = parseInt(action.split('_')[1]);
          const btns = await page.$$('.btn-simulate');
          if (btns[idx]) await btns[idx].click();
        }} else if (action === 'api_page') {{
          await page.goto('http://localhost:8000/', {{ waitUntil: 'networkidle0' }});
        }}
        await new Promise(r => setTimeout(r, 200));
      }}
    }}
    
    const fname = path.join(FRAME_DIR, 'frame_' + String(f).padStart(5, '0') + '.png');
    await page.screenshot({{ path: fname }});
    frame++;
  }}

  await browser.close();
  console.log('Captured ' + frame + ' frames over ' + TOTAL_DURATION.toFixed(1) + 's');
}})();
"""
    script_path = '/tmp/record-narrated.js'
    with open(script_path, 'w') as f:
        f.write(script)
    return script_path

async def main():
    # Generate English narration with better voice
    print("=== English (en-US-AndrewMultilingualNeural) ===")
    en_dir = '/tmp/narration-en-v2'
    en_durations = await generate_segments(SCENES_EN, "en-US-AndrewMultilingualNeural", en_dir, "EN")
    
    # Concatenate with pauses
    en_audio = '/tmp/narration-en-full.mp3'
    en_total, en_timestamps = concat_audio_with_pauses(en_dir, en_durations, en_audio)
    print(f"  Total EN audio: {en_total:.1f}s")
    
    # Generate Spanish with Elena (female) instead of Tomas
    print("\n=== Spanish (es-MX-DaliaNeural) ===")
    es_dir = '/tmp/narration-es-v2'
    es_durations = await generate_segments(SCENES_ES, "es-MX-DaliaNeural", es_dir, "ES", rate="-3%")
    
    es_audio = '/tmp/narration-es-full.mp3'
    es_total, es_timestamps = concat_audio_with_pauses(es_dir, es_durations, es_audio)
    print(f"  Total ES audio: {es_total:.1f}s")
    
    # Record English video (longer version, synced to narration)
    print("\n=== Recording English video ===")
    en_script = generate_puppeteer_script(SCENES_EN, en_timestamps, en_durations, en_total, 'en')
    subprocess.run(['node', en_script], check=True)
    
    # Encode EN video + audio
    en_output = os.path.join(WORKSPACE, 'simulai-demo-en.mp4')
    subprocess.run([
        'ffmpeg', '-y',
        '-framerate', '4',
        '-i', '/tmp/demo-frames-narrated/frame_%05d.png',
        '-i', en_audio,
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k',
        '-vf', 'scale=1400:900',
        '-shortest',
        en_output
    ], capture_output=True, check=True)
    size = os.path.getsize(en_output) / 1024 / 1024
    print(f"  EN video: {size:.1f}MB")
    
    # Record Spanish video
    print("\n=== Recording Spanish video ===")
    es_script = generate_puppeteer_script(SCENES_ES, es_timestamps, es_durations, es_total, 'es')
    subprocess.run(['node', es_script], check=True)
    
    es_output = os.path.join(WORKSPACE, 'simulai-demo-es.mp4')
    subprocess.run([
        'ffmpeg', '-y',
        '-framerate', '4',
        '-i', '/tmp/demo-frames-narrated/frame_%05d.png',
        '-i', es_audio,
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k',
        '-vf', 'scale=1400:900',
        '-shortest',
        es_output
    ], capture_output=True, check=True)
    size = os.path.getsize(es_output) / 1024 / 1024
    print(f"  ES video: {size:.1f}MB")
    
    print("\nDone!")

asyncio.run(main())
