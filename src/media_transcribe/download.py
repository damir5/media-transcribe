from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


AUDIO_EXTENSIONS = {".mp3", ".m4a", ".wav", ".aac", ".ogg", ".flac", ".mp4", ".mkv", ".webm"}


def is_youtube_url(source: str) -> bool:
    return any(host in source for host in ("youtube.com/", "youtu.be/", "m.youtube.com/"))


def is_remote_audio(source: str) -> bool:
    source_lower = source.lower()
    return source_lower.startswith(("http://", "https://")) and any(
        source_lower.endswith(ext) for ext in AUDIO_EXTENSIONS
    )


def ensure_audio_local(source: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    if source.startswith(("http://", "https://")):
        out_path = out_dir / "source-audio.mp3"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                source,
                "-vn",
                "-acodec",
                "libmp3lame",
                str(out_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return out_path

    local = Path(source).expanduser().resolve()
    copied = out_dir / local.name
    if copied != local:
        shutil.copy2(local, copied)
    return copied


def download_youtube_audio(url: str, out_dir: Path) -> tuple[Path, dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(out_dir / "youtube.%(ext)s")
    metadata = subprocess.run(
        ["yt-dlp", "--dump-json", "--no-playlist", url],
        check=True,
        capture_output=True,
        text=True,
    ).stdout

    subprocess.run(
        [
            "yt-dlp",
            "--extract-audio",
            "--audio-format",
            "mp3",
            "--no-playlist",
            "-o",
            output_template,
            url,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    audio_path = next(out_dir.glob("youtube.*"))
    import json

    return audio_path, json.loads(metadata)
