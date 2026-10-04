#!/bin/sh
# Add or replace the photo of a work in all three web sizes.
# macOS (uses the built-in `sips`); on Linux ImageMagick `convert` is used instead.
#
#   scripts/add_image.sh <work-number> "<path to original photo>"
#   e.g. scripts/add_image.sh 47 "$HOME/Library/Mobile Documents/com~apple~CloudDocs/Art/Mind Mechanics/Mind Mechanics no. 4/MM47.jpg"
#
# Then add/adjust the entry in data/works.json and run: python3 scripts/build.py && python3 scripts/check.py
set -e
[ $# -eq 2 ] || { echo "usage: $0 <number> <photo>"; exit 1; }
NAME=$(printf "mm-%02d.jpg" "$1")
SRC="$2"
cd "$(dirname "$0")/.."
for PX in 1600 1200 800; do
  mkdir -p "images/$PX"
  OUT="images/$PX/$NAME"
  if command -v sips >/dev/null 2>&1; then
    sips -s format jpeg -s formatOptions 78 --resampleWidth "$PX" "$SRC" --out "$OUT" >/dev/null
  else
    convert "$SRC" -auto-orient -resize "${PX}x" +profile '!icc,*' -quality 78 -interlace Plane "$OUT"
  fi
  echo "wrote $OUT"
done
