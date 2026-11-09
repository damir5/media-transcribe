from __future__ import annotations

import re


def _seconds(value: str) -> float:
    stamp = value.strip().replace(",", ".")
    try:
        numbers = [float(part) for part in stamp.split(":")]
    except ValueError:
        return 0.0
    if len(numbers) == 3:
        return round(numbers[0] * 3600 + numbers[1] * 60 + numbers[2], 3)
    if len(numbers) == 2:
        return round(numbers[0] * 60 + numbers[1], 3)
    return round(numbers[0], 3) if numbers else 0.0


def parse_srt_segments(srt: str) -> list[dict]:
    """Timed segments from SRT, so captions keep the timestamps whisper segments have."""
    segments: list[dict] = []
    block: list[str] = []
    for raw_line in [*srt.splitlines(), ""]:
        line = raw_line.strip()
        if line:
            block.append(line)
            continue
        if len(block) >= 2 and "-->" in block[1]:
            start, _, end = block[1].partition("-->")
            body = " ".join(
                re.sub(r"<[^>]+>", "", part).strip() for part in block[2:]
            ).strip()
            if body:
                segments.append({
                    "start": _seconds(start),
                    "end": _seconds(end),
                    "text": body,
                })
        block = []
    return segments


def normalize_srt_text(srt: str) -> str:
    cleaned: list[str] = []
    for raw_line in srt.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if re.fullmatch(r"\d+", line):
            continue
        if "-->" in line:
            continue
        line = re.sub(r"<[^>]+>", "", line).strip()
        if not line:
            continue
        if cleaned and cleaned[-1] == line:
            continue
        cleaned.append(line)
    return " ".join(cleaned).strip()
