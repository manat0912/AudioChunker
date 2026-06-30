import io
import os
import re
import shutil
import zipfile
import subprocess
import tempfile
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Audiochunker", page_icon="icon.png", layout="centered")

# Where chunks are written. Kept inside the app folder so they survive a rerun.
WORK_DIR = Path(tempfile.gettempdir()) / "audiochunker"
WORK_DIR.mkdir(parents=True, exist_ok=True)


def have_binary(name: str) -> bool:
    return shutil.which(name) is not None


def probe_duration(path: Path) -> float | None:
    """Return audio duration in seconds using ffprobe, or None if unknown."""
    if not have_binary("ffprobe"):
        return None
    try:
        out = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=True,
        )
        return float(out.stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        return None


def human_time(seconds: float) -> str:
    seconds = int(round(seconds))
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:d}:{s:02d}"


def chunk_audio(input_path: Path, segment_seconds: int, out_dir: Path) -> list[Path]:
    """Split input_path into segment_seconds-long clips using ffmpeg.

    Uses stream copy (-c copy) so any input format is preserved without
    re-encoding, matching the input container/codec.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*"):
        old.unlink()

    ext = input_path.suffix or ".mp3"
    output_pattern = str(out_dir / f"{input_path.stem}_%03d{ext}")

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-nostdin",
        "-loglevel", "error",
        "-y",
        "-i", str(input_path),
        "-f", "segment",
        "-segment_time", str(segment_seconds),
        "-c", "copy",
        output_pattern,
    ]
    subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, check=True)

    return sorted(out_dir.glob(f"{input_path.stem}_*{ext}"))


def build_zip(files: list[Path]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as zf:
        for f in files:
            zf.write(f, arcname=f.name)
    buf.seek(0)
    return buf.read()


# ----------------------------------------------------------------------------
# UI
# ----------------------------------------------------------------------------
st.title("🎧 Audiochunker")
st.caption("Slice any audio file into fixed-length clips and export them all at once.")

if not have_binary("ffmpeg"):
    st.error(
        "ffmpeg was not found on PATH. On Pinokio it is provided through conda — "
        "make sure the environment that runs this app has ffmpeg available."
    )
    st.stop()

uploaded = st.file_uploader(
    "Import audio (any format)",
    type=None,
    accept_multiple_files=False,
    help="mp3, wav, flac, m4a, ogg, aac, opus, wma… anything ffmpeg can read.",
)

segment_seconds = st.slider(
    "Chunk length (seconds)",
    min_value=10,
    max_value=60,
    value=60,
    step=10,
    help="Each chunk covers a different consecutive segment of the source audio.",
)

if uploaded is not None:
    # Persist the upload to disk so ffmpeg can read it.
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", uploaded.name) or "audio"
    input_path = WORK_DIR / safe_name
    input_path.write_bytes(uploaded.getbuffer())

    duration = probe_duration(input_path)
    cols = st.columns(3)
    cols[0].metric("File", input_path.name)
    if duration is not None:
        cols[1].metric("Duration", human_time(duration))
        n_expected = max(1, -(-int(duration) // segment_seconds))  # ceil div
        cols[2].metric("Chunks", f"~{n_expected}")

    st.audio(uploaded)

    if st.button("✂️  Chunk audio", type="primary", use_container_width=True):
        out_dir = WORK_DIR / "chunks"
        try:
            with st.spinner("Chunking with ffmpeg…"):
                chunks = chunk_audio(input_path, segment_seconds, out_dir)
            if not chunks:
                st.warning("No chunks were produced. Is the file a valid audio file?")
            else:
                st.session_state["chunks"] = [str(p) for p in chunks]
                st.session_state["seg"] = segment_seconds
                st.success(f"Created {len(chunks)} chunk(s) of {segment_seconds}s each.")
        except subprocess.CalledProcessError as e:
            st.error("ffmpeg failed:\n\n" + (e.stderr or str(e)))

# Render results (kept in session_state so download buttons don't wipe them).
chunk_paths = [Path(p) for p in st.session_state.get("chunks", []) if Path(p).exists()]
if chunk_paths:
    st.divider()
    st.subheader(f"Chunks ({len(chunk_paths)})")

    st.download_button(
        "⬇️  Export ALL clips (.zip)",
        data=build_zip(chunk_paths),
        file_name="audiochunker_clips.zip",
        mime="application/zip",
        type="primary",
        use_container_width=True,
    )

    seg = st.session_state.get("seg", segment_seconds)
    for i, p in enumerate(chunk_paths):
        start = i * seg
        with st.container(border=True):
            st.markdown(f"**{p.name}** — starts at `{human_time(start)}`")
            data = p.read_bytes()
            st.audio(data)
            st.download_button(
                "Download",
                data=data,
                file_name=p.name,
                key=f"dl_{i}",
            )
