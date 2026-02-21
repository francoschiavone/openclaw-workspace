# TOOLS.md - Local Notes

## Video Production Settings

### Audio Mix — Demo Videos (approved by Franco 2026-02-18)
Final settings for videos with narration + background music:

```
Voice: volume=1.8 (80% boost from original)
Music: volume=0.03 (3% of original)
Music fade in: 2s
Music fade out: 6s (starts 6s before the end)
```

### Background Music
- **Current track:** Pixabay CC0 corporate/tech (`https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3?filename=corporate-music-free-no-copyright-14206.mp3`)
- No copyright, no attribution required
- Style: corporate/tech, dynamic, keeps the viewer awake
- Saved at: `/tmp/track1.mp3` (re-download if lost)

### ffmpeg command for mixing
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

### Send media via WhatsApp
```bash
openclaw message send --channel whatsapp --target "+5493415634531" --media <path>
```
Without `--message` if Franco doesn't want a caption.

## SSH Hosts
_(pending)_

## Cameras
_(pending)_
