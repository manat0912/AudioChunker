# Audiochunker

A [Pinokio](https://pinokio.computer) app that slices **any** audio file into
fixed-length clips and lets you export them all at once.

## What it does

- **Import any audio format** — mp3, wav, flac, m4a, ogg, aac, opus, wma… anything ffmpeg can read.
- **Pick a chunk length** with a seconds slider: `10 / 20 / 30 / 40 / 50 / 60` seconds.
- **Segment the whole file** into consecutive clips, each covering a different part of the source
  (e.g. a 5-minute file at 60s gives you 5 clips: `0:00`, `1:00`, `2:00`, `3:00`, `4:00`).
- **Export all clips at once** as a single `.zip`, or download any clip individually.

Chunking uses ffmpeg's segment muxer with stream copy (no re-encoding), so output
clips keep the exact codec/container of the input:

```python
import subprocess

input_file = "input.mp3"
output_pattern = "output_%03d.mp3"

subprocess.run([
    "ffmpeg",
    "-i", input_file,
    "-f", "segment",
    "-segment_time", "60",
    "-c", "copy",
    output_pattern,
])
```

## Requirements

- **ffmpeg / ffprobe** on PATH. On Pinokio these come from the bundled conda
  environment, so no extra install is needed.
- Python 3.12 (created automatically by `install.js`).

## Install / Run (Pinokio)

1. **Install** — creates the `env` virtualenv and installs Streamlit.
2. **Start** — launches the Streamlit web UI; click **Open Web UI**.

> ffmpeg/ffprobe must be on PATH. On Pinokio they come from the bundled conda
> environment, so no extra install step is required.

## Run manually (without Pinokio)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Make sure `ffmpeg` is installed and on your PATH.
