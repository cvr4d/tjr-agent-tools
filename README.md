# TJR Agent Tools

A collection of Python tools for searching and processing YouTube subtitles from the TJR trading channel.

## 🛠️ Tools

| Tool | Description |
|------|-------------|
| `tjr_context.py` | Exact phrase search in subtitle files (`.en.srt`) |
| `tjr_fuzzy.py` | Fuzzy search with similarity scoring |
| `sub.py` | Generate SRT subtitles from any video/audio using faster-whisper |
| `frame.py` | Add rounded corners + black frame around a video |

## 📋 Requirements

- Python 3.10+
- ffmpeg (in PATH)
- yt-dlp

## 🚀 Install

```bash
git clone https://github.com/cvr4d/tjr-agent-tools.git
cd tjr-agent-tools

# Create virtual environment
python3 -m venv venv
source venv/bin/activate      # Linux/macOS
# venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

📥 Download Subtitles

Use yt-dlp to download all English subtitles from a YouTube channel:
bash

yt-dlp --skip-download \
       --write-auto-subs --write-subs \
       --sub-langs "en" \
       --convert-subs srt \
       -o "%(id)s.%(ext)s" \
       "https://www.youtube.com/@TJRTrades/videos"

⚙️ Configuration

Set the TJR_SUBTITLES environment variable to point to your subtitles folder:
bash

export TJR_SUBTITLES=/path/to/subtitles

Default: ~/TJR_SUBTITLES
💻 Usage
Exact search
bash

python tjr_context.py "fair value gap"

Fuzzy search
bash

python tjr_fuzzy.py "fair value gapp"

Generate subtitles from video
bash

python sub.py video.mp4 5    # 5 = max words per line

Add frame to video
bash

python frame.py video.mp4


