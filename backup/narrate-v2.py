"""Add narration to v2 demo video"""
import sys, os, subprocess, asyncio
sys.path.insert(0, '/home/node/.openclaw/workspace/pylibs')
import edge_tts

WS = '/home/node/.openclaw/workspace'

# Scenes with timestamps matching the video recording
# Total ~54s video
NARRATION_EN = [
    (0.5, "Welcome to SimulAI. Your industrial digital twins, powered by artificial intelligence."),
    (5.0, "The main dashboard gives you a bird's eye view. Six digital twins, each monitoring a real piece of equipment. Health scores, uptime, power consumption, all in real time."),
    (14.0, "Let's drill into the coolant pump. It's in critical condition at 43 percent health. Live sensors show temperature at 89 degrees and dangerous vibration levels."),
    (19.0, "The AI predicts failure within days. High risk, high confidence. But it also tells you how much money you'll save by acting now."),
    (24.5, "Now the CNC lathe. Healthy at 87 percent. The 24-hour sensor history shows stable operation. Low risk prediction."),
    (30.0, "The alerts center consolidates all warnings across your fleet. Two critical alerts on the pump, filter degradation on the HVAC, and trending issues on the conveyor."),
    (36.5, "The simulation lab is where it gets interesting. Pick any twin, set a scenario, adjust parameters, and run a thousand Monte Carlo simulations in seconds."),
    (42.0, "The AI shows you exactly what happens. Energy costs, wear rates, throughput changes, and failure risk. Every decision backed by data."),
    (47.5, "Fleet analytics give you the big picture. 142 thousand dollars in costs avoided. 97 percent prediction accuracy. Performance rankings across all twins."),
    (52.0, "SimulAI. Industrial decisions with certainty, not intuition."),
]

NARRATION_ES = [
    (0.5, "Bienvenido a SimulAI. Tus gemelos digitales industriales, potenciados por inteligencia artificial."),
    (5.0, "El dashboard principal te da una vista panorámica. Seis gemelos digitales, cada uno monitoreando un equipo real. Salud, uptime, consumo energético. Todo en tiempo real."),
    (14.0, "Entremos a la bomba de refrigerante. Está en estado crítico, 43 por ciento de salud. Los sensores muestran 89 grados de temperatura y niveles peligrosos de vibración."),
    (19.0, "La inteligencia artificial predice falla en días. Riesgo alto, alta confianza. Pero también te dice cuánto dinero ahorrás actuando ahora."),
    (24.5, "Ahora el torno CNC. Saludable al 87 por ciento. El historial de 24 horas muestra operación estable. Predicción de riesgo bajo."),
    (30.0, "El centro de alertas consolida todos los avisos de tu flota. Dos alertas críticas en la bomba, degradación de filtro en el HVAC, y tendencias preocupantes en la cinta transportadora."),
    (36.5, "El laboratorio de simulación es donde la cosa se pone interesante. Elegí cualquier twin, configurá un escenario, ajustá parámetros, y corré mil simulaciones Monte Carlo en segundos."),
    (42.0, "La IA te muestra exactamente qué pasa. Costos energéticos, tasas de desgaste, cambios en producción y riesgo de falla. Cada decisión respaldada por datos."),
    (47.5, "Las analíticas de flota te dan el panorama completo. 142 mil dólares en costos evitados. 97 por ciento de precisión en predicciones. Rankings de rendimiento de todos los twins."),
    (52.0, "SimulAI. Decisiones industriales con certeza, no con intuición."),
]

async def generate_and_mix(narration, voice, lang, rate="-3%"):
    seg_dir = f'/tmp/narration-v2-{lang}'
    os.makedirs(seg_dir, exist_ok=True)
    
    print(f"\n=== {lang.upper()} ({voice}) ===")
    
    # Generate segments
    for i, (ts, text) in enumerate(narration):
        f = os.path.join(seg_dir, f'seg_{i:02d}.mp3')
        c = edge_tts.Communicate(text, voice, rate=rate)
        await c.save(f)
        dur = subprocess.run(['ffprobe','-v','quiet','-show_entries','format=duration','-of','csv=p=0', f], capture_output=True, text=True)
        print(f"  {i}: {float(dur.stdout.strip()):.1f}s @ {ts}s - {text[:50]}...")
    
    # Build ffmpeg filter to place each segment at its timestamp
    video = os.path.join(WS, 'simulai-demo-v2-silent.mp4')
    inputs = ['-i', video]
    filter_parts = []
    
    for i, (ts, _) in enumerate(narration):
        seg = os.path.join(seg_dir, f'seg_{i:02d}.mp3')
        inputs.extend(['-i', seg])
        delay_ms = int(ts * 1000)
        filter_parts.append(f"[{i+1}:a]adelay={delay_ms}|{delay_ms},volume=1.0[a{i}]")
    
    mix_inputs = ''.join(f'[a{i}]' for i in range(len(narration)))
    filter_parts.append(f"{mix_inputs}amix=inputs={len(narration)}:duration=longest:dropout_transition=0[aout]")
    
    output = os.path.join(WS, f'simulai-demo-v2-{lang}.mp4')
    cmd = ['ffmpeg', '-y'] + inputs + [
        '-filter_complex', ';'.join(filter_parts),
        '-map', '0:v', '-map', '[aout]',
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-shortest', output
    ]
    
    print(f"  Mixing...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ERROR: {r.stderr[-300:]}")
    else:
        size = os.path.getsize(output) / 1024 / 1024
        print(f"  Output: {output} ({size:.1f}MB)")

async def main():
    await generate_and_mix(NARRATION_EN, "en-US-AndrewMultilingualNeural", "en")
    await generate_and_mix(NARRATION_ES, "es-MX-DaliaNeural", "es")
    print("\nDone!")

asyncio.run(main())
