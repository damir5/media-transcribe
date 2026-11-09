from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .normalize import normalize_srt_text, parse_srt_segments


def fetch_youtube_captions(
    url: str, out_dir: Path
) -> tuple[str | None, dict, list[dict]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    meta_raw = subprocess.run(
        ["yt-dlp", "--dump-json", "--no-playlist", url],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    meta = json.loads(meta_raw)

    subprocess.run(
        [
            "yt-dlp",
            "--write-auto-subs",
            "--write-subs",
            "--sub-lang",
            "en.*",
            "--convert-subs",
            "srt",
            "--skip-download",
            "--no-playlist",
            "-o",
            str(out_dir / "%(id)s"),
            url,
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    srt_files = sorted(out_dir.glob("*.srt"))
    if not srt_files:
        return None, meta, []

    raw = srt_files[0].read_text(encoding="utf-8")
    text = normalize_srt_text(raw)
    if len(text) < 80:
        return None, meta, []
    return text, meta, parse_srt_segments(raw)
