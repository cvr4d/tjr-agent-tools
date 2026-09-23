#!/usr/bin/env python3

import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""
frame: Add rounded corners + black frame around a video.
Portable version - requires ffmpeg + Pillow.
"""

import os
import sys
import subprocess
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Error: Pillow not installed.")
    print("Install with: pip install Pillow")
    sys.exit(1)


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running: {' '.join(cmd)}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()


def main():
    if len(sys.argv) < 2:
        print("Usage: python frame.py video.mp4 [output.mp4]")
        sys.exit(1)

    input_file = sys.argv[1]
    if not Path(input_file).exists():
        print(f"Error: input not found: {input_file}")
        sys.exit(1)

    stem, ext = os.path.splitext(input_file)
    output = sys.argv[2] if len(sys.argv) > 2 else f"{stem}_framed{ext}"

    tools_dir = Path.home() / ".ffmpeg-tools"
    tools_dir.mkdir(exist_ok=True)

    W = int(run([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width", "-of", "csv=p=0", input_file
    ]))
    H = int(run([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=height", "-of", "csv=p=0", input_file
    ]))
    print(f"→ Video dimensions: {W}x{H}")

    radius = max(80, int(H * 0.15))
    mask = tools_dir / f"mask_{W}x{H}_r{radius}.png"

    if not mask.exists():
        print(f"→ Creating mask for {W}x{H} (radius={radius})...")
        img = Image.new("L", (W, H), 0)
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([(0, 0), (W - 1, H - 1)],
                                radius=radius, fill=255)
        img.save(mask)
        print(f"✓ Mask created: {mask}")

    FW = W + 480
    FH = H + 480
    print(f"→ Output: {FW}x{FH}")

    filter_complex = (
        f"[0:v][1:v]alphamerge[rounded];"
        f"color=c=black:s={FW}x{FH}[bg];"
        f"[bg][rounded]overlay=(W-w)/2:(H-h)/2:shortest=1:format=auto[out]"
    )

    subprocess.run([
        "ffmpeg", "-y", "-i", input_file, "-i", str(mask),
        "-filter_complex", filter_complex,
        "-map", "[out]", "-map", "0:a?",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-c:a", "copy",
        output
    ], check=True)

    print(f"\n✓ Done: {output}")


if __name__ == "__main__":
    main()
