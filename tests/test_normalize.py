from media_transcribe.normalize import normalize_srt_text


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
