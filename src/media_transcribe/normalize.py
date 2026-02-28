from __future__ import annotations

import re


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
