#!/usr/bin/env python3
"""
sub: Generate subtitles from a video/audio file using faster-whisper.
Portable version - works on Windows, Linux, macOS.
"""

import os
import sys
from pathlib import Path

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("Error: faster-whisper not installed.")
    print("Install with: pip install faster-whisper")
    sys.exit(1)


def fmt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def main():
    if len(sys.argv) < 2:
        print("Usage: python sub.py video.mp4 [max_words_per_line]")
        sys.exit(1)

    video_file = sys.argv[1]
    max_words = int(sys.argv[2]) if len(sys.argv) > 2 else 4

    if not Path(video_file).exists():
        print(f"Error: input not found: {video_file}")
        sys.exit(1)

    print(f"Extracting subtitles from: {video_file} ...")
    print(f"Max words per line: {max_words}")

    model_size = os.environ.get("WHISPER_MODEL", "small")
    device = os.environ.get("WHISPER_DEVICE", "cpu")
    compute_type = os.environ.get("WHISPER_COMPUTE", "int8")

    print(f"Loading model: {model_size} on {device} ({compute_type})")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    segments, _ = model.transcribe(
        video_file,
        language="en",
        word_timestamps=True,
    )

    out_file = os.path.splitext(video_file)[0] + ".srt"
    i = 1

    with open(out_file, "w", encoding="utf-8") as f:
        for segment in segments:
            words = segment.words or []
            buffer = []
            for word in words:
                buffer.append(word)
                if len(buffer) >= max_words:
                    start = buffer[0].start
                    end = buffer[-1].end
                    text = " ".join(w.word.strip() for w in buffer)
                    f.write(
                        f"{i}\n{fmt_time(start)} --> {fmt_time(end)}\n"
                        f"{text}\n\n"
                    )
                    i += 1
                    buffer = []
            if buffer:
                start = buffer[0].start
                end = buffer[-1].end
                text = " ".join(w.word.strip() for w in buffer)
                f.write(
                    f"{i}\n{fmt_time(start)} --> {fmt_time(end)}\n"
                    f"{text}\n\n"
                )
                i += 1

    print(f"Saved: {out_file}")


if __name__ == "__main__":
    main()
