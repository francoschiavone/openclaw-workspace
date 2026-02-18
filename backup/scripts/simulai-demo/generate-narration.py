"""
Generate narrated demo video for SimulAI
Uses Edge TTS (Microsoft neural voices) + ffmpeg
"""
import sys
sys.path.insert(0, '/home/node/.openclaw/workspace/pylibs')

import asyncio
import edge_tts
import subprocess
import os

WORKSPACE = '/home/node/.openclaw/workspace'

# Narration script synced to video scenes (timed to 4fps recording)
# Each segment: (text, start_time_seconds, voice)
SCRIPT_ES = [
    ("SimulAI. Plataforma de Digital Twins con Inteligencia Artificial.", 0.5),
    ("Acá ves el dashboard principal. Cinco gemelos digitales monitoreando equipos industriales en tiempo real.", 3.5),
    ("Cada twin muestra el estado de salud, sensores activos y el status operativo del equipo.", 7.0),
    ("Mirá la bomba de refrigerante. Está en rojo. 43 por ciento de salud. Estado degradado.", 10.5),
    ("Ahora usamos la IA para predecir fallas. El CNC está estable, riesgo bajo.", 15.0),
    ("Simulamos un escenario. Qué pasa si subimos las RPM un 40 por ciento? Energía sube 53 por ciento. Desgaste sube 85 por ciento. La IA recomienda precaución.", 18.5),
    ("El HVAC tiene riesgo medio. Falla estimada en 15 días. Degradación gradual del filtro.", 24.0),
    ("La bomba de refrigerante es crítica. Riesgo alto. Falla en 3 días. Sobretemperatura y vibración excesiva. 71 mil dólares en costos evitados si actuás ahora.", 27.5),
    ("SimulAI. Decisiones industriales con certeza, no con intuición.", 33.0),
]

SCRIPT_EN = [
    ("SimulAI. Digital Twins platform powered by Artificial Intelligence.", 0.5),
    ("Here's the main dashboard. Five digital twins monitoring industrial equipment in real time.", 3.5),
    ("Each twin shows health status, active sensors, and operational state.", 7.0),
    ("Look at the coolant pump. It's in red. 43 percent health. Degraded status.", 10.5),
    ("Now we use AI to predict failures. The CNC lathe is stable, low risk.", 15.0),
    ("We simulate a scenario. What if we increase RPM by 40 percent? Energy goes up 53 percent. Wear increases 85 percent. AI recommends caution.", 18.5),
    ("The HVAC unit shows medium risk. Estimated failure in 15 days. Gradual filter degradation.", 24.0),
    ("The coolant pump is critical. High risk. Failure in 3 days. Overheating and excessive vibration. 71 thousand dollars in costs avoided if you act now.", 27.5),
    ("SimulAI. Industrial decisions with certainty, not intuition.", 33.0),
]

async def generate_audio(script, voice, output_dir, lang):
    """Generate individual audio segments"""
    os.makedirs(output_dir, exist_ok=True)
    
    for i, (text, start_time) in enumerate(script):
        output_file = os.path.join(output_dir, f"segment_{i:02d}.mp3")
        communicate = edge_tts.Communicate(text, voice, rate="-5%")
        await communicate.save(output_file)
        print(f"  [{lang}] Segment {i}: {text[:50]}...")
    
    return len(script)

def mix_audio_video(segments_dir, script, video_path, output_path):
    """Mix audio segments with video using ffmpeg"""
    # Build complex filter for mixing audio segments at specific times
    inputs = ['-i', video_path]
    filter_parts = []
    
    for i, (text, start_time) in enumerate(script):
        seg_file = os.path.join(segments_dir, f"segment_{i:02d}.mp3")
        inputs.extend(['-i', seg_file])
        # Delay each segment to its start time (in milliseconds)
        delay_ms = int(start_time * 1000)
        filter_parts.append(f"[{i+1}:a]adelay={delay_ms}|{delay_ms}[a{i}]")
    
    # Mix all audio streams
    mix_inputs = ''.join(f'[a{i}]' for i in range(len(script)))
    filter_parts.append(f"{mix_inputs}amix=inputs={len(script)}:duration=longest[aout]")
    
    filter_complex = ';'.join(filter_parts)
    
    cmd = [
        'ffmpeg', '-y',
        *inputs,
        '-filter_complex', filter_complex,
        '-map', '0:v',
        '-map', '[aout]',
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',
        output_path
    ]
    
    print(f"  Mixing {len(script)} segments with video...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ffmpeg error: {result.stderr[-500:]}")
        return False
    return True

async def main():
    video_path = os.path.join(WORKSPACE, 'simulai-demo.mp4')
    
    # Generate Spanish narration (Argentine voice)
    print("Generating Spanish narration (es-AR-TomasNeural)...")
    es_dir = '/tmp/narration-es'
    await generate_audio(SCRIPT_ES, "es-AR-TomasNeural", es_dir, "ES")
    
    # Generate English narration  
    print("Generating English narration (en-US-AndrewMultilingualNeural)...")
    en_dir = '/tmp/narration-en'
    await generate_audio(SCRIPT_EN, "en-US-AndrewMultilingualNeural", en_dir, "EN")
    
    # Mix Spanish version
    print("\nMixing Spanish video...")
    es_output = os.path.join(WORKSPACE, 'simulai-demo-es.mp4')
    if mix_audio_video(es_dir, SCRIPT_ES, video_path, es_output):
        size = os.path.getsize(es_output) / 1024 / 1024
        print(f"  Spanish video: {es_output} ({size:.1f}MB)")
    
    # Mix English version
    print("Mixing English video...")
    en_output = os.path.join(WORKSPACE, 'simulai-demo-en.mp4')
    if mix_audio_video(en_dir, SCRIPT_EN, video_path, en_output):
        size = os.path.getsize(en_output) / 1024 / 1024
        print(f"  English video: {en_output} ({size:.1f}MB)")
    
    print("\nDone!")

asyncio.run(main())
