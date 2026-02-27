#!/bin/bash
set -e

SCREENSHOTS="/tmp/demo-screenshots"
NARRATIONS="/tmp/demo-narrations"
MUSIC="/tmp/bg-music.mp3"
OUTPUT="/tmp/lumber-hris-demo-v3.mp4"
SEGMENTS_DIR="/tmp/demo-segments"
CONCAT_LIST="/tmp/demo-concat.txt"
SILENT_VIDEO="/tmp/demo-silent.mp4"
NARRATION_FULL="/tmp/demo-narration-full.mp3"

rm -rf "$SEGMENTS_DIR"
mkdir -p "$SEGMENTS_DIR"

echo "=== Step 1: Create silent video segments ==="

for i in $(seq 0 22); do
  idx=$(printf "%02d" $i)
  screenshot=$(ls "$SCREENSHOTS"/*.png | sort | sed -n "$((i+1))p")
  narration="$NARRATIONS/${idx}.mp3"
  segment="$SEGMENTS_DIR/seg_${idx}.mp4"
  
  [ ! -f "$screenshot" ] || [ ! -f "$narration" ] && continue
  
  raw_dur=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$narration" 2>/dev/null)
  duration=$(python3 -c "print(round(${raw_dur} + 0.5, 2))")
  
  echo "  [$idx] ${duration}s"
  
  ffmpeg -y -loop 1 -i "$screenshot" \
    -c:v libx264 -tune stillimage -pix_fmt yuv420p \
    -vf "scale=1440:900:force_original_aspect_ratio=decrease,pad=1440:900:(ow-iw)/2:(oh-ih)/2:color=#f0f2f5" \
    -t "$duration" -an \
    "$segment" 2>/dev/null
done

echo ""
echo "=== Step 2: Concat silent video ==="
> "$CONCAT_LIST"
for seg in $(ls "$SEGMENTS_DIR"/seg_*.mp4 | sort); do
  echo "file '$seg'" >> "$CONCAT_LIST"
done

ffmpeg -y -f concat -safe 0 -i "$CONCAT_LIST" -c copy "$SILENT_VIDEO" 2>/dev/null
TOTAL_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$SILENT_VIDEO")
echo "  Silent video: ${TOTAL_DUR}s"

echo ""
echo "=== Step 3: Build narration track with gaps ==="

# Calculate cumulative offsets and build narration track
python3 << 'PYEOF'
import subprocess, os, json

narr_dir = "/tmp/demo-narrations"
output = "/tmp/demo-narration-full.mp3"

# Get durations of each narration + gap
segments = []
for i in range(23):
    f = os.path.join(narr_dir, f"{i:02d}.mp3")
    r = subprocess.run(["ffprobe","-v","quiet","-show_entries","format=duration","-of","csv=p=0", f], capture_output=True, text=True)
    dur = float(r.stdout.strip())
    segments.append((f, dur))

# Build ffmpeg filter: place each narration sequentially with 0.5s gap
filter_parts = []
inputs = []
for i, (f, dur) in enumerate(segments):
    inputs.extend(["-i", f])
    # Calculate cumulative offset
    offset = sum(d + 0.5 for _, d in segments[:i])
    delay_ms = int(offset * 1000)
    filter_parts.append(f"[{i}:a]adelay={delay_ms}|{delay_ms},volume=1.8[a{i}]")

mix = "".join(f"[a{i}]" for i in range(23))
filter_parts.append(f"{mix}amix=inputs=23:duration=longest:dropout_transition=0[out]")

cmd = ["ffmpeg", "-y"] + inputs + [
    "-filter_complex", ";".join(filter_parts),
    "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "192k",
    output
]
subprocess.run(cmd, capture_output=True)
dur = subprocess.run(["ffprobe","-v","quiet","-show_entries","format=duration","-of","csv=p=0", output], capture_output=True, text=True)
print(f"  Narration track: {float(dur.stdout.strip()):.1f}s")
PYEOF

echo ""
echo "=== Step 4: Mix voice + music + video ==="

# Get video duration for music fade
FADE_START=$(python3 -c "print(round(${TOTAL_DUR} - 6, 2))")

ffmpeg -y \
  -i "$SILENT_VIDEO" \
  -i "$NARRATION_FULL" \
  -i "$MUSIC" \
  -filter_complex "\
    [1:a]apad=whole_dur=${TOTAL_DUR}[voice];\
    [2:a]aloop=loop=-1:size=2e+09,atrim=0:${TOTAL_DUR},volume=0.03,afade=t=in:d=2,afade=t=out:st=${FADE_START}:d=6[music];\
    [voice][music]amix=inputs=2:duration=first:dropout_transition=2[aout]" \
  -map 0:v -map "[aout]" \
  -c:v libx264 -crf 23 -preset medium \
  -c:a aac -b:a 128k \
  -shortest \
  "$OUTPUT" 2>/dev/null

SIZE=$(du -sh "$OUTPUT" | awk '{print $1}')
FINAL_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$OUTPUT")
echo ""
echo "✅ Video created: $OUTPUT"
echo "   Duration: ${FINAL_DUR}s"
echo "   Size: $SIZE"
