#!/bin/bash
# Assemble demo video: screenshots + narration
set -e

SCREENSHOTS="/tmp/demo-screenshots"
NARRATIONS="/tmp/demo-narrations"
OUTPUT="/tmp/lumber-hris-demo.mp4"
SEGMENTS_DIR="/tmp/demo-segments"
CONCAT_LIST="/tmp/demo-concat.txt"

rm -rf "$SEGMENTS_DIR"
mkdir -p "$SEGMENTS_DIR"

echo "Creating video segments..."

for i in $(seq 0 22); do
  idx=$(printf "%02d" $i)
  
  # Get screenshot name (sorted order)
  screenshot=$(ls "$SCREENSHOTS"/*.png | sort | sed -n "$((i+1))p")
  narration="$NARRATIONS/${idx}.mp3"
  segment="$SEGMENTS_DIR/seg_${idx}.mp4"
  
  if [ ! -f "$screenshot" ] || [ ! -f "$narration" ]; then
    echo "  ⚠️ Missing files for segment $idx"
    continue
  fi
  
  # Get audio duration + 0.8s padding
  raw_dur=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$narration" 2>/dev/null)
  duration=$(python3 -c "print(round(${raw_dur} + 0.8, 2))")
  
  echo "  [$idx] $(basename $screenshot) + $(basename $narration) → ${duration}s"
  
  # Create video segment: image for duration + audio
  ffmpeg -y -loop 1 -i "$screenshot" -i "$narration" \
    -c:v libx264 -tune stillimage -pix_fmt yuv420p \
    -vf "scale=1440:900:force_original_aspect_ratio=decrease,pad=1440:900:(ow-iw)/2:(oh-ih)/2:color=#f0f2f5" \
    -c:a aac -b:a 128k -ar 44100 \
    -t "$duration" \
    -shortest \
    "$segment" 2>/dev/null
done

# Create concat list
echo "Concatenating segments..."
> "$CONCAT_LIST"
for seg in $(ls "$SEGMENTS_DIR"/seg_*.mp4 | sort); do
  echo "file '$seg'" >> "$CONCAT_LIST"
done

# Concatenate all segments
ffmpeg -y -f concat -safe 0 -i "$CONCAT_LIST" \
  -c:v libx264 -crf 23 -preset medium \
  -c:a aac -b:a 128k \
  "$OUTPUT" 2>/dev/null

# Get final stats
duration=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$OUTPUT" 2>/dev/null)
size=$(du -sh "$OUTPUT" | awk '{print $1}')
echo ""
echo "✅ Video created: $OUTPUT"
echo "   Duration: ${duration}s"
echo "   Size: $size"
