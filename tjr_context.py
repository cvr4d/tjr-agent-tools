#!/usr/bin/env python3
"""
tjr-context: Search YouTube subtitles for exact phrases.
Portable version - works on Windows, Linux, macOS.
"""

import sys
import re
import os
from pathlib import Path

ROOT = Path(os.environ.get("TJR_SUBTITLES",
            os.path.expanduser("~/TJR_SUBTITLES")))


def parse_time(s):
    m = re.fullmatch(r"(\d+):(\d{2}):(\d{2}),(\d{3})", s.strip())
    if not m:
        raise ValueError(s)
    h, mi, sec, ms = map(int, m.groups())
    return ((h * 60 + mi) * 60 + sec) * 1000 + ms


def parse_arg(s):
    if s.isdigit():
        return int(s)
    if "-" in s and "-->" not in s:
        a, b = s.split("-", 1)
        try:
            return parse_time(a), parse_time(b)
        except ValueError:
            pass
    try:
        return parse_time(s)
    except ValueError:
        return None


def fmt(ms):
    ms = max(0, int(ms))
    h, rem = divmod(ms, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def clean(text):
    text = re.sub(r"\[[^\]]*\]", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def words(text):
    return re.findall(r"[a-z0-9']+", text.lower())


def yt_id(filename):
    m = re.search(r"\[([^\]]+)\]\.en\.srt$", filename)
    if m:
        return m.group(1)
    m = re.search(r"^([A-Za-z0-9_-]{11})\.en\.srt$", filename)
    return m.group(1) if m else "unknown"


def read_srt(path):
    text = path.read_text(errors="ignore")
    blocks = []
    pattern = re.compile(
        r"(?m)^\s*(\d+)\s*\n"
        r"(\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+"
        r"(\d{2}:\d{2}:\d{2},\d{3}).*?\n"
        r"(.*?)(?=\n\s*\n|\Z)",
        re.S,
    )
    for m in pattern.finditer(text):
        start = parse_time(m.group(2))
        end = parse_time(m.group(3))
        body = clean(m.group(4))
        if not body:
            continue
        blocks.append((start, end, body))

    result = []
    for block in blocks:
        if result:
            prev = result[-1]
            if (block[2].lower() == prev[2].lower()
                and abs(block[0] - prev[0]) <= 100):
                continue
        result.append(block)
    return result


def candidate_files(query):
    q = list(dict.fromkeys(words(query)))
    if not q:
        return []
    anchors = sorted(q, key=lambda x: (-len(x), x))[:2]
    pattern = re.compile(
        r"\b(?:" + "|".join(re.escape(x) for x in anchors) + r")\b",
        re.IGNORECASE
    )
    results = []
    for srt_file in ROOT.rglob("*.en.srt"):
        try:
            text = srt_file.read_text(errors="ignore")
            if pattern.search(text):
                results.append(srt_file)
        except Exception:
            continue
    return results


def locate_match(blocks, query):
    q = words(query)
    if not q:
        return None
    tokens = []
    token_block = []
    for index, block in enumerate(blocks):
        for token in words(block[2]):
            tokens.append(token)
            token_block.append(index)
    n = len(q)
    if n > len(tokens):
        return None
    for i in range(len(tokens) - n + 1):
        if tokens[i] != q[0]:
            continue
        if tokens[i:i + n] == q:
            first = token_block[i]
            last = token_block[i + n - 1]
            return first, last
    return None


def context(blocks, start, end):
    before, after = [], []
    for block in blocks:
        if block[1] <= start and start - block[1] <= 3000:
            before.append(block)
        if block[0] >= end and block[0] - end <= 3000:
            after.append(block)
    return before[-5:], after[:5]


def print_result(path, blocks, first, last):
    start = blocks[first][0]
    end = blocks[last][1]
    before, after = context(blocks, start, end)
    video = f"https://www.youtube.com/watch?v={yt_id(path.name)}"

    print()
    print(f"FILE: {path}")
    print(f"VIDEO: {video}")
    print(f"TIMESTAMP: {fmt(start)} --> {fmt(end)}")
    print("\nMATCH:")
    for i in range(first, last + 1):
        print(f"{fmt(blocks[i][0])} --> {fmt(blocks[i][1])} | {blocks[i][2]}")
    if before:
        print("\nCONTEXT BEFORE:")
        for b in before:
            print(f"{fmt(b[0])} --> {fmt(b[1])} | {b[2]}")
    if after:
        print("\nCONTEXT AFTER:")
        for b in after:
            print(f"{fmt(b[0])} --> {fmt(b[1])} | {b[2]}")
    print()


def search(query):
    files = candidate_files(query)
    for path in files:
        try:
            blocks = read_srt(path)
            match = locate_match(blocks, query)
            if match:
                print_result(path, blocks, *match)
        except Exception:
            continue


def exact_file_mode(path, start_arg, end_arg=None):
    if not path.exists():
        print(f"File not found: {path}")
        return
    blocks = read_srt(path)
    start = parse_arg(start_arg)
    if isinstance(start, tuple):
        end = start[1]
        start = start[0]
    else:
        end = parse_arg(end_arg) if end_arg else start
    if start is None:
        print("Invalid timestamp.")
        return
    if end is None:
        end = start
    matched = [i for i, b in enumerate(blocks)
               if b[1] >= start and b[0] <= end]
    if not matched:
        print("No subtitles found in that range.")
        return
    print_result(path, blocks, matched[0], matched[-1])


def main():
    if len(sys.argv) < 2:
        print('Usage: tjr-context "search phrase"')
        print('       tjr-context file.en.srt START [END]')
        sys.exit(1)
    if not ROOT.exists():
        print(f"Error: subtitle folder not found: {ROOT}")
        print(f"Set env var TJR_SUBTITLES or create {ROOT}")
        sys.exit(1)
    first = sys.argv[1]
    if first.endswith(".en.srt") and Path(first).exists():
        exact_file_mode(
            Path(first),
            sys.argv[2] if len(sys.argv) > 2 else "0",
            sys.argv[3] if len(sys.argv) > 3 else None,
        )
        return
    search(" ".join(sys.argv[1:]))


if __name__ == "__main__":
    main()
