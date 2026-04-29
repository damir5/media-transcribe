# media-transcribe

Local transcript extraction for YouTube and audio sources.

## Usage

```bash
./media-transcribe captions youtube https://youtu.be/example
./media-transcribe transcribe https://youtu.be/example --out-dir ./out
./media-transcribe transcribe ./episode.mp3 --out-dir ./out
```

The CLI emits normalized transcript JSON and stores audio/transcript artifacts in `--out-dir`.

## Install

```bash
ln -sf "$(pwd)/media-transcribe" ~/.local/bin/media-transcribe
```

The wrapper resolves its real location, so it works both from this directory and through a symlink.
