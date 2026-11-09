from __future__ import annotations

import argparse
import json
from pathlib import Path

from .download import download_youtube_audio, ensure_audio_local, is_remote_audio, is_youtube_url
from .normalize import normalize_srt_text
from .stt import transcribe_with_faster_whisper
from .youtube import fetch_youtube_captions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Transcribe media sources to normalized JSON")
    subparsers = parser.add_subparsers(dest="command", required=True)

    captions = subparsers.add_parser("captions", help="Extract normalized captions")
    captions_subparsers = captions.add_subparsers(dest="captions_command", required=True)
    youtube = captions_subparsers.add_parser("youtube", help="Fetch YouTube captions")
    youtube.add_argument("source")
    youtube.add_argument("--out-dir", default="./out")

    transcribe = subparsers.add_parser("transcribe", help="Transcribe YouTube/audio inputs")
    transcribe.add_argument("source")
    transcribe.add_argument("--out-dir", default="./out")
    transcribe.add_argument("--model", default="large-v3-turbo")

    normalize = subparsers.add_parser("normalize-srt", help="Normalize SRT to plain text")
    normalize.add_argument("path")
    return parser


def json_print(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def handle_captions_youtube(source: str, out_dir: Path) -> int:
    text, meta, segments = fetch_youtube_captions(source, out_dir)
    payload = {
        "source": source,
        "sourceType": "youtube",
        "title": meta.get("title"),
        "language": "en",
        "durationSeconds": meta.get("duration"),
        "text": text,
        "segments": segments,
        "method": "youtube-captions" if text else "none",
    }
    json_print(payload)
    return 0 if text else 1


def handle_transcribe(source: str, out_dir: Path, model: str) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)

    title = None
    source_type = "audio-file"
    transcript_method = "faster-whisper"

    if is_youtube_url(source):
        source_type = "youtube"
        text, meta, segments = fetch_youtube_captions(source, out_dir / "captions")
        title = meta.get("title")
        if text:
            payload = {
                "source": source,
                "sourceType": source_type,
                "title": title,
                "language": "en",
                "durationSeconds": meta.get("duration"),
                "text": text,
                "segments": segments,
                "method": "youtube-captions",
                "artifacts": {},
            }
            json_print(payload)
            return 0
        audio_path, meta = download_youtube_audio(source, out_dir / "audio")
        title = meta.get("title")
    else:
        if is_remote_audio(source):
            source_type = "audio-url"
        audio_path = ensure_audio_local(source, out_dir / "audio")

    transcript = transcribe_with_faster_whisper(audio_path, model_name=model)
    transcript_path = out_dir / "transcript.txt"
    transcript_path.write_text(transcript["text"] + "\n", encoding="utf-8")

    payload = {
        "source": source,
        "sourceType": source_type,
        "title": title or audio_path.stem,
        "language": transcript["language"],
        "durationSeconds": transcript["durationSeconds"],
        "text": transcript["text"],
        "segments": transcript["segments"],
        "method": transcript_method,
        "artifacts": {
            "audioPath": str(audio_path),
            "transcriptTxtPath": str(transcript_path),
        },
    }
    json_print(payload)
    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "captions" and args.captions_command == "youtube":
        raise SystemExit(handle_captions_youtube(args.source, Path(args.out_dir).resolve()))

    if args.command == "transcribe":
        raise SystemExit(handle_transcribe(args.source, Path(args.out_dir).resolve(), args.model))

    if args.command == "normalize-srt":
        print(normalize_srt_text(Path(args.path).read_text(encoding="utf-8")))
        raise SystemExit(0)

    raise SystemExit(2)
