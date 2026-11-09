from media_transcribe.normalize import normalize_srt_text, parse_srt_segments


def test_parse_srt_segments_keeps_timestamps():
    raw = """1
00:00:00,000 --> 00:00:02,500
Hello <i>there</i>

2
00:01:03,250 --> 00:01:05,000
World
"""
    assert parse_srt_segments(raw) == [
        {"start": 0.0, "end": 2.5, "text": "Hello there"},
        {"start": 63.25, "end": 65.0, "text": "World"},
    ]


def test_normalize_srt_text():
    raw = """1
00:00:00,000 --> 00:00:01,000
Hello

2
00:00:01,000 --> 00:00:02,000
<i>Hello</i>

3
00:00:02,000 --> 00:00:03,000
World
"""
    assert normalize_srt_text(raw) == "Hello World"
