# StemSplit — Research & Market Report

**Fecha**: Febrero 2026
**Autor**: Claude (Opus 4.6) para Franco Schiavone

---

## Resumen Ejecutivo

La separación de pistas de audio (stem separation) es un mercado en crecimiento impulsado por músicos, DJs, content creators y la industria del karaoke. Los modelos open source actuales (especialmente Demucs v4 de Meta) alcanzan calidad profesional comparable a soluciones pagas.

### Oportunidad
- Gap significativo entre herramientas gratuitas (limitadas o complicadas) y pagas ($8-25/mes)
- UVR5 es la única opción free con calidad profesional, pero requiere instalación desktop
- No existe una web app free, sin límites, con calidad Demucs v4

---

## 1. Estado del Arte — Modelos Open Source

### Top 5 por Calidad (SDR en MUSDB18-HQ)

| # | Modelo | SDR | Arquitectura | Organización |
|---|--------|-----|-------------|-------------|
| 1 | **HTDemucs ft** | 9.2 dB | U-Net + Transformer híbrido | Meta AI |
| 2 | **Mel-Band RoFormer** | 9.0+ dB | Transformer + Mel-bands | ByteDance |
| 3 | **SCNet** | 9.0 dB | Sparse Compression | ICASSP 2024 |
| 4 | **BS-RoFormer** | 8.8 dB | Transformer + Band-split | ByteDance |
| 5 | **BSRNN** | 8.2-9.0 dB | Band-split RNN | Microsoft |

### Recomendación: **Demucs v4 (HTDemucs)**
- Mejor balance calidad/facilidad de uso
- API Python simple (`pip install demucs`)
- MIT license
- Modelo pre-entrenado de ~80MB
- 4 stems (vocals, drums, bass, other) + variante de 6 stems

*(Reporte detallado: `stem-separation-report.md`)*

---

## 2. Competidores Comerciales

### Principales Players

| Competidor | Precio | Stems | Calidad | UX | Target |
|-----------|--------|-------|---------|-----|--------|
| **LALAL.AI** | $7.5-15/mes | 10 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Profesionales |
| **Moises.ai** | $3.99-24.99/mes | 10+ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Músicos, mobile |
| **AudioShake** | ~$1/min | Todos | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Enterprise |
| **UVR5** | FREE | Todos | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Técnicos |
| **Fadr** | FREE ilimitado | 16 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | DJs |
| **StemRoller** | FREE | 4 | ⭐⭐⭐⭐ | ⭐⭐⭐ | Casual |
| **Splitter.ai** | Free tier | 2-5 | ⭐⭐⭐ | ⭐⭐⭐ | Casual |

### Gaps en el Mercado
1. **No hay web app free + alta calidad + sin límites**: Fadr es free pero calidad media
2. **UVR5 es técnicamente superior pero requiere desktop install**
3. **Ninguno ofrece WAV downloads gratis** (excepto UVR5 local)
4. **Preview instantáneo** antes de procesar: casi nadie lo hace bien

*(Reportes detallados: `stem_separation_competitors_analysis.md` y subdocumentos)*

---

## 3. Análisis de UX/UI

### Patrones Ganadores
- **Dark theme** con acento vibrante (cyan, naranja, o verde)
- **Upload drag & drop** directo en hero
- **Progress bar** con porcentaje y tip rotativo
- **Stem cards** con play/download individual + Download All ZIP
- **Waveform animation** durante procesamiento

### Color Palettes de Referencia
- **Cyberpunk/Tech** (nuestra elección): `#00D4FF` cyan + `#8B5CF6` purple + `#0A0A0F` dark
- Spotify-style: `#1DB954` green + `#121212` dark
- LALAL.AI: `#FF4D00` orange + white/dark toggle

### Stack Frontend Recomendado
- Vanilla HTML/CSS/JS para MVP (sin build step)
- Next.js + Tailwind + shadcn/ui para producción
- WaveSurfer.js para waveforms interactivos

*(Reporte detallado: `stem-separation-ux-analysis.md`)*

---

## 4. Arquitectura Técnica

### Stack del MVP (Implementado)
- **Backend**: FastAPI + Demucs v4 + Python 3.11
- **Frontend**: Vanilla HTML/CSS/JS (dark theme, responsive)
- **Processing**: Async subprocess con WebSocket progress
- **Output**: MP3 320kbps (4 stems)

### Performance (CPU ARM64, sin GPU)
- 5s audio → 6s procesamiento
- 30s audio → 15s procesamiento
- ~1.5x duración del audio (peor caso)
- Con GPU: ~20x más rápido (10-20s para cualquier canción)

### Para Escalar a Producción
- Worker queue (Celery + Redis)
- GPU inference (RunPod $0.16/hr o Replicate $0.015/canción)
- Chunked upload con presigned URLs
- CDN para delivery de stems

*(Reporte detallado: `stem-separation-architecture.md`)*

---

## 5. StemSplit — El MVP

### ¿Qué es?
Una web app que separa cualquier archivo de audio en 4 stems (vocals, drums, bass, other) usando Demucs v4 de Meta.

### Features
- ✅ Upload drag & drop (MP3, WAV, FLAC, OGG, M4A)
- ✅ Procesamiento con Demucs v4 (HTDemucs)
- ✅ Progress en real-time (WebSocket)
- ✅ 4 stems: vocals, drums, bass, other
- ✅ Play/preview individual de cada stem
- ✅ Download individual o ZIP
- ✅ UI dark theme profesional (no "vibe-coded")
- ✅ 100% free, sin signup, sin límites
- ✅ Responsive design

### Archivos
```
stem-app/
├── server.py          # FastAPI backend
├── static/
│   ├── index.html     # Landing + app UI
│   ├── style.css      # Dark theme design system
│   └── app.js         # Frontend logic
├── demo/
│   ├── stemsplit-demo.mp4   # Video demo
│   ├── 01-landing.png       # Screenshot: landing
│   ├── 02-processing.png    # Screenshot: processing
│   ├── 04-results.png       # Screenshot: results
│   └── ...
└── RESEARCH-REPORT.md       # Este archivo
```

### Cómo Correr
```bash
# Activar venv
. .venv-stem/bin/activate

# Correr server
cd stem-app && python3 server.py

# Abrir http://localhost:8765
```

---

## 6. Próximos Pasos (si se quiere productizar)

### Inmediato
1. Agregar WaveSurfer.js para waveforms interactivos
2. Agregar modelo de 6 stems (guitar, piano)
3. Deploy con GPU para velocidad real-time

### Medio Plazo
4. Landing page con dominio propio
5. Batch processing
6. API pública
7. Formato WAV/FLAC como opción

### Largo Plazo
8. Modelo propio fine-tuned (Mel-Band RoFormer)
9. Real-time preview antes de procesar completo
10. Mobile app (React Native)
11. Monetización: free tier + pro con GPU priority

---

*Reportes de research completos en el workspace:*
- `stem-separation-report.md` — 14 herramientas open source analizadas
- `stem_separation_competitors_analysis.md` — 12 competidores comerciales
- `stem-separation-ux-analysis.md` — Análisis UX/UI de 8 sitios
- `stem-separation-architecture.md` — Arquitectura técnica detallada
