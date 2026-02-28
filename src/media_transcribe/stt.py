from __future__ import annotations

from pathlib import Path


def transcribe_with_faster_whisper(audio_path: Path, model_name: str) -> dict:
    from faster_whisper import WhisperModel

    model = WhisperModel(model_name, device="auto", compute_type="int8")
    segments, info = model.transcribe(str(audio_path), vad_filter=True)

    normalized_segments = []
    text_parts: list[str] = []
    for segment in segments:
        text = segment.text.strip()
        if not text:
            continue
        normalized_segments.append({
            "start": round(segment.start, 3),
            "end": round(segment.end, 3),
            "text": text,
        })
        text_parts.append(text)

    return {
        "language": info.language,
        "durationSeconds": round(info.duration, 3) if info.duration else None,
        "text": " ".join(text_parts).strip(),
        "segments": normalized_segments,
    }
