# TOOLS.md - Local Notes

## Video Production Settings

### Audio Mix — Demo Videos (aprobado por Franco 2026-02-18)
Configuración final para videos con narración + música de fondo:

```
Voz: volume=1.8 (boost 80% del original)
Música: volume=0.03 (3% del original)
Fade in música: 2s
Fade out música: 6s (empieza 6s antes del final)
```

### Música de fondo
- **Pista actual:** Pixabay CC0 corporate/tech (`https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3?filename=corporate-music-free-no-copyright-14206.mp3`)
- Sin derechos de autor, sin atribución necesaria
- Estilo: corporate/tech, dinámica, mantiene despierto al viewer
- Guardada en: `/tmp/track1.mp3` (re-descargar si se pierde)

### Comando ffmpeg para mezclar
```bash
ffmpeg -y \
  -i <video_con_voz.mp4> \
  -i <musica.mp3> \
  -filter_complex "\
    [0:a]volume=1.8[voice];\
    [1:a]atrim=0:<duracion_video>,volume=0.03,afade=t=in:d=2,afade=t=out:st=<duracion-6>:d=6[music];\
    [voice][music]amix=inputs=2:duration=first:dropout_transition=2[out]" \
  -map 0:v -map "[out]" \
  -c:v copy -c:a aac -b:a 128k \
  <output.mp4>
```

### Enviar media por WhatsApp
```bash
openclaw message send --channel whatsapp --target "+5493415634531" --media <path>
```
Sin `--message` si Franco no quiere caption.

## SSH Hosts
_(pendiente)_

## Cameras
_(pendiente)_
