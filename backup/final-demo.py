"""
SimulAI Demo v2 - Final version with zero audio overlap
Strategy: generate audio first (sequential), then record video to match
"""
import sys, os, subprocess, asyncio, json
sys.path.insert(0, '/home/node/.openclaw/workspace/pylibs')
import edge_tts

WS = '/home/node/.openclaw/workspace'
FPS = 6
PAUSE = 0.6  # seconds between segments

# Each entry: (narration_text, puppeteer_action)
SCRIPT_EN = [
    ("Welcome to SimulAI. Your industrial digital twins, powered by artificial intelligence.", "dashboard_hold"),
    ("The main dashboard gives you a bird's eye view. Six digital twins monitoring industrial equipment in real time. Health scores, uptime, and power consumption at a glance.", "dashboard_scroll"),
    ("Let's look at the coolant pump. It's critical. Only 43 percent health. Live sensors show dangerous temperature and vibration.", "twin_pump"),
    ("The AI predicts failure within days. High confidence. Sixty four thousand dollars in avoidable costs if you act now.", "twin_pump_scroll"),
    ("The CNC lathe is a different story. 87 percent health. Stable operation. Low risk.", "twin_cnc"),
    ("The alerts center consolidates warnings across your entire fleet. Critical, warning, and informational. All prioritized.", "alerts"),
    ("The simulation lab. Pick any twin, set your parameters, and run a thousand Monte Carlo simulations in seconds.", "sim_config"),
    ("The AI shows the full impact. Energy, wear, throughput, and failure risk. Every decision backed by data.", "sim_run"),
    ("Fleet analytics. 142 thousand dollars saved this year. 97 percent prediction accuracy. Full performance rankings.", "analytics"),
    ("SimulAI. Industrial decisions with certainty, not intuition.", "dashboard_finale"),
]

SCRIPT_ES = [
    ("Bienvenido a SimulAI. Gemelos digitales industriales potenciados por inteligencia artificial.", "dashboard_hold"),
    ("El dashboard principal te da una vista panorámica. Seis gemelos digitales. Salud, uptime y consumo energético de un vistazo.", "dashboard_scroll"),
    ("Miremos la bomba de refrigerante. Está crítica. 43 por ciento de salud. Sensores muestran temperatura y vibración peligrosas.", "twin_pump"),
    ("La IA predice falla en días. Alta confianza. Sesenta y cuatro mil dólares en costos evitables si actuás ahora.", "twin_pump_scroll"),
    ("El torno CNC es otra historia. 87 por ciento de salud. Operación estable. Riesgo bajo.", "twin_cnc"),
    ("El centro de alertas consolida avisos de toda tu flota. Críticas, advertencias e informativas. Todo priorizado.", "alerts"),
    ("El laboratorio de simulación. Elegí un twin, configurá parámetros, y corré mil simulaciones Monte Carlo en segundos.", "sim_config"),
    ("La IA muestra el impacto completo. Energía, desgaste, producción y riesgo de falla. Cada decisión respaldada por datos.", "sim_run"),
    ("Analíticas de flota. 142 mil dólares ahorrados este año. 97 por ciento de precisión predictiva. Rankings completos.", "analytics"),
    ("SimulAI. Decisiones industriales con certeza, no con intuición.", "dashboard_finale"),
]


async def generate_sequential_audio(script, voice, lang, rate="-3%"):
    """Generate audio segments and calculate sequential timestamps"""
    seg_dir = f'/tmp/final-{lang}'
    os.makedirs(seg_dir, exist_ok=True)
    
    segments = []
    current_time = 0.3  # small initial delay
    
    for i, (text, action) in enumerate(script):
        fpath = os.path.join(seg_dir, f'seg_{i:02d}.mp3')
        comm = edge_tts.Communicate(text, voice, rate=rate)
        await comm.save(fpath)
        
        # Get duration
        r = subprocess.run(['ffprobe','-v','quiet','-show_entries','format=duration','-of','csv=p=0', fpath],
                          capture_output=True, text=True)
        dur = float(r.stdout.strip())
        
        segments.append({
            'file': fpath,
            'start': current_time,
            'duration': dur,
            'action': action,
            'text': text[:50]
        })
        print(f"  [{lang}] {i}: {dur:.1f}s @ {current_time:.1f}s - {text[:50]}...")
        
        current_time += dur + PAUSE
    
    total_duration = current_time + 1.0  # 1s buffer at end
    print(f"  Total: {total_duration:.1f}s")
    
    # Concatenate audio with proper timing using adelay
    inputs = []
    filter_parts = []
    for i, seg in enumerate(segments):
        inputs.extend(['-i', seg['file']])
        delay_ms = int(seg['start'] * 1000)
        filter_parts.append(f"[{i}:a]adelay={delay_ms}|{delay_ms}[a{i}]")
    
    mix_inputs = ''.join(f'[a{i}]' for i in range(len(segments)))
    filter_parts.append(f"{mix_inputs}amix=inputs={len(segments)}:duration=longest:dropout_transition=0[aout]")
    
    audio_path = f'/tmp/final-audio-{lang}.mp3'
    cmd = ['ffmpeg', '-y'] + inputs + [
        '-filter_complex', ';'.join(filter_parts),
        '-map', '[aout]', '-c:a', 'libmp3lame', '-b:a', '192k',
        audio_path
    ]
    subprocess.run(cmd, capture_output=True)
    
    return segments, total_duration, audio_path


def create_puppeteer_script(segments, total_duration, lang):
    """Create JS script for recording video synced to audio timing"""
    scenes = []
    for seg in segments:
        scenes.append({
            'start': seg['start'],
            'duration': seg['duration'],
            'action': seg['action']
        })
    
    script = f"""
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');
const {{ execSync }} = require('child_process');

const FRAME_DIR = '/tmp/final-frames-{lang}';
const FPS = {FPS};
const TOTAL = {total_duration};
const SCENES = {json.dumps(scenes)};

(async () => {{
  if (fs.existsSync(FRAME_DIR)) execSync('rm -rf ' + FRAME_DIR);
  fs.mkdirSync(FRAME_DIR, {{ recursive: true }});

  const browser = await puppeteer.launch({{
    executablePath: '/usr/bin/chromium',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
    headless: 'new'
  }});
  const page = await browser.newPage();
  await page.setViewport({{ width: 1440, height: 900 }});
  await page.goto('http://localhost:8000/dashboard', {{ waitUntil: 'networkidle0' }});

  let frame = 0;
  let triggered = new Set();
  const totalFrames = Math.ceil(TOTAL * FPS);

  for (let f = 0; f < totalFrames; f++) {{
    const t = f / FPS;

    for (let s = 0; s < SCENES.length; s++) {{
      if (!triggered.has(s) && t >= SCENES[s].start && t < SCENES[s].start + 0.5) {{
        triggered.add(s);
        const a = SCENES[s].action;
        console.log('  ' + t.toFixed(1) + 's: ' + a);

        try {{
          if (a === 'dashboard_hold') {{
            // already there
          }} else if (a === 'dashboard_scroll') {{
            await page.evaluate(() => window.scrollTo({{ top: 400, behavior: 'smooth' }}));
          }} else if (a === 'twin_pump') {{
            await page.goto('http://localhost:8000/twin/pump-001', {{ waitUntil: 'networkidle0' }});
          }} else if (a === 'twin_pump_scroll') {{
            await page.evaluate(() => window.scrollTo({{ top: 500, behavior: 'smooth' }}));
          }} else if (a === 'twin_cnc') {{
            await page.goto('http://localhost:8000/twin/cnc-lathe-001', {{ waitUntil: 'networkidle0' }});
          }} else if (a === 'alerts') {{
            await page.goto('http://localhost:8000/alerts', {{ waitUntil: 'networkidle0' }});
          }} else if (a === 'sim_config') {{
            await page.goto('http://localhost:8000/simulation', {{ waitUntil: 'networkidle0' }});
          }} else if (a === 'sim_run') {{
            const btn = await page.$('#sim-btn');
            if (btn) await btn.click();
          }} else if (a === 'analytics') {{
            await page.goto('http://localhost:8000/analytics', {{ waitUntil: 'networkidle0' }});
            await new Promise(r => setTimeout(r, 500));
            await page.evaluate(() => window.scrollTo({{ top: 300, behavior: 'smooth' }}));
          }} else if (a === 'dashboard_finale') {{
            await page.goto('http://localhost:8000/dashboard', {{ waitUntil: 'networkidle0' }});
          }}
        }} catch(e) {{ console.log('    error: ' + e.message); }}
        await new Promise(r => setTimeout(r, 150));
      }}
    }}

    const fname = path.join(FRAME_DIR, 'frame_' + String(f).padStart(5, '0') + '.png');
    await page.screenshot({{ path: fname }});
    frame++;
  }}

  await browser.close();
  console.log('Captured ' + frame + ' frames (' + (frame/FPS).toFixed(1) + 's)');
}})();
"""
    script_path = f'/tmp/record-final-{lang}.js'
    with open(script_path, 'w') as f:
        f.write(script)
    return script_path


async def main():
    # EN
    print("=== ENGLISH ===")
    en_segs, en_total, en_audio = await generate_sequential_audio(
        SCRIPT_EN, "en-US-AndrewMultilingualNeural", "en", rate="-2%"
    )
    
    print(f"\nRecording EN video ({en_total:.0f}s)...")
    en_js = create_puppeteer_script(en_segs, en_total, "en")
    r = subprocess.run(['node', en_js], capture_output=True, text=True,
                      env={**os.environ, 'NODE_PATH': f'{WS}/node_modules'})
    print(r.stdout[-200:] if r.stdout else r.stderr[-200:])
    
    # Encode
    en_out = os.path.join(WS, 'simulai-demo-v2-en.mp4')
    subprocess.run([
        'ffmpeg', '-y',
        '-framerate', str(FPS), '-i', f'/tmp/final-frames-en/frame_%05d.png',
        '-i', en_audio,
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k',
        '-vf', 'scale=1440:900', '-shortest', en_out
    ], capture_output=True)
    print(f"EN: {os.path.getsize(en_out)/1024/1024:.1f}MB")
    
    # ES
    print("\n=== SPANISH ===")
    es_segs, es_total, es_audio = await generate_sequential_audio(
        SCRIPT_ES, "es-MX-DaliaNeural", "es", rate="-2%"
    )
    
    print(f"\nRecording ES video ({es_total:.0f}s)...")
    es_js = create_puppeteer_script(es_segs, es_total, "es")
    r = subprocess.run(['node', es_js], capture_output=True, text=True,
                      env={**os.environ, 'NODE_PATH': f'{WS}/node_modules'})
    print(r.stdout[-200:] if r.stdout else r.stderr[-200:])
    
    es_out = os.path.join(WS, 'simulai-demo-v2-es.mp4')
    subprocess.run([
        'ffmpeg', '-y',
        '-framerate', str(FPS), '-i', f'/tmp/final-frames-es/frame_%05d.png',
        '-i', es_audio,
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k',
        '-vf', 'scale=1440:900', '-shortest', es_out
    ], capture_output=True)
    print(f"ES: {os.path.getsize(es_out)/1024/1024:.1f}MB")
    
    print("\nDone!")

asyncio.run(main())
