#!/usr/bin/env python3
"""
tjr-fuzzy: Fuzzy search in YouTube subtitles.
Portable version - requires rapidfuzz.
"""

import sys
import re
import os
from pathlib import Path

try:
    from rapidfuzz import process, fuzz
except ImportError:
    print("Error: rapidfuzz not installed.")
    print("Install with: pip install rapidfuzz")
    sys.exit(1)

ROOT = Path(os.environ.get("TJR_SUBTITLES",
            os.path.expanduser("~/TJR_SUBTITLES")))


def clean(s):
    s = re.sub(r"\[[^\]]*\]", " ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_time(s):
    h, m, sm = s.split(":")
    sec, ms = sm.split(",")
    return ((int(h) * 60 + int(m)) * 60 + int(sec)) * 1000 + int(ms)


def fmt(ms):
    h, r = divmod(ms, 3600000)
    m, r = divmod(r, 60000)
    s, ms = divmod(r, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def read_srt(path):
    text = path.read_text(errors="ignore")
    pattern = re.compile(
        r"(?m)^\s*\d+\s*\n"
        r"(\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+"
        r"(\d{2}:\d{2}:\d{2},\d{3}).*?\n"
        r"(.*?)(?=\n\s*\n|\Z)", re.S
    )
    blocks = []
    for m in pattern.finditer(text):
        body = clean(m.group(3))
        if body:
            blocks.append((parse_time(m.group(1)),
                           parse_time(m.group(2)), body))
    return blocks


def video_id(path):
    m = re.search(r"\[([^\]]+)\]\.en\.srt$", path.name)
    if m:
        return m.group(1)
    m = re.search(r"^([A-Za-z0-9_-]{11})\.en\.srt$", path.name)
    return m.group(1) if m else "unknown"


def main():
    if len(sys.argv) < 2:
        print('Usage: tjr-fuzzy "phrase"')
        sys.exit(1)
    if not ROOT.exists():
        print(f"Error: subtitle folder not found: {ROOT}")
        sys.exit(1)

    query = clean(" ".join(sys.argv[1:]))
    qwords = query.lower().split()

    anchors = sorted(set(qwords), key=len, reverse=True)[:2]
    if anchors:
        pattern = re.compile(
            r"\b(?:" + "|".join(re.escape(x) for x in anchors) + r")\b",
            re.IGNORECASE
        )
        files = [f for f in ROOT.rglob("*.en.srt")
                 if pattern.search(f.read_text(errors="ignore"))]
    else:
        files = list(ROOT.rglob("*.en.srt"))

    if not files:
        print("No candidate files found.")
        return

    results = []
    for path in files:
        blocks = read_srt(path)
        if not blocks:
            continue
        text = " ".join(b[2] for b in blocks)
        match = process.extractOne(query, [text],
                                    scorer=fuzz.partial_ratio)
        if not match:
            continue
        score = match[1]
        if score >= 55:
            results.append((score, path, blocks, text))

    results.sort(key=lambda x: x[0], reverse=True)
    if not results:
        print(f"No fuzzy matches found for: {query}")
        return

    for score, path, blocks, text in results[:10]:
        best = process.extractOne(
            query, [b[2] for b in blocks],
            scorer=fuzz.partial_ratio
        )
        idx = best[2] if best else 0
        first = max(0, idx - 2)
        last = min(len(blocks) - 1, idx + 2)

        print()
        print(f"SCORE: {score:.0f}%")
        print(f"FILE: {path}")
        print(f"VIDEO: https://www.youtube.com/watch?v={video_id(path)}")
        print(f"TIMESTAMP: {fmt(blocks[first][0])} --> "
              f"{fmt(blocks[last][1])}")
        print("\nMATCH:")
        for i in range(first, last + 1):
            print(f"{fmt(blocks[i][0])} --> "
                  f"{fmt(blocks[i][1])} | {blocks[i][2]}")
        print()


if __name__ == "__main__":
    main()
