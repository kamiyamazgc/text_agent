import os
import sys
import types
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docpipe.extractors.youtube import YouTubeExtractor  # noqa: E402


class DummyAudioExtractor:
    def __init__(self, model: str = "large") -> None:
        pass

    def extract(self, source: str, **kwargs):
        return {
            "text": "AUDIO TEXT",
            "metadata": {"file_name": Path(source).name, "model": "dummy", "source_type": "audio"},
        }


def test_can_handle_youtube():
    extractor = YouTubeExtractor(Path("temp"))
    assert extractor.can_handle("https://youtube.com/watch?v=abc123")
    assert extractor.can_handle("https://youtu.be/abc123")
    assert not extractor.can_handle("https://example.com")


def test_extract_with_captions(monkeypatch, tmp_path):
    extractor = YouTubeExtractor(tmp_path)
    monkeypatch.setattr(extractor, "_get_video_id", lambda url: "abc123")
    monkeypatch.setattr(extractor, "_download_captions", lambda vid: "CAPTION TEXT")
    monkeypatch.setattr(extractor, "_download_audio", lambda vid: None)
    result = extractor.extract("https://youtube.com/watch?v=abc123")
    assert result["text"] == "CAPTION TEXT"
    assert result["metadata"]["caption_used"]
    assert result["metadata"]["language"] == "en"
    assert result["metadata"]["needs_translation"]


def test_extract_with_audio(monkeypatch, tmp_path):
    audio_path = tmp_path / "abc123.mp3"
    audio_path.write_text("dummy")
    extractor = YouTubeExtractor(tmp_path)
    monkeypatch.setattr(extractor, "_get_video_id", lambda url: "abc123")
    monkeypatch.setattr(extractor, "_download_captions", lambda vid: None)
    monkeypatch.setattr(extractor, "_download_audio", lambda vid: audio_path)
    monkeypatch.setattr("docpipe.extractors.youtube.AudioExtractor", DummyAudioExtractor)
    result = extractor.extract("https://youtube.com/watch?v=abc123")
    assert result["text"] == "AUDIO TEXT"
    assert not result["metadata"]["caption_used"]
    assert result["metadata"]["language"] == "en"
    assert result["metadata"]["needs_translation"]


def test_extract_japanese_caption(monkeypatch, tmp_path):
    extractor = YouTubeExtractor(tmp_path)
    monkeypatch.setattr(extractor, "_get_video_id", lambda url: "abc123")
    monkeypatch.setattr(extractor, "_download_captions", lambda vid: "これは日本語です")
    monkeypatch.setattr(extractor, "_download_audio", lambda vid: None)
    result = extractor.extract("https://youtu.be/abc123")
    assert result["metadata"]["language"] == "ja"
    assert not result["metadata"]["needs_translation"]


def test_download_captions_with_auto_lang(monkeypatch, tmp_path):
    video_id = "abc123"

    class DummyDL:
        def __init__(self, opts=None):
            self.opts = opts or {}

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        def extract_info(self, url, download=False):
            return {"automatic_captions": {"fr": [{"url": "dummy"}]}}

        def download(self, urls):
            lang = self.opts.get("subtitleslangs", ["fr"])[0]
            outtmpl = self.opts.get("outtmpl", "")
            caption_file = Path(outtmpl.replace("%(ext)s", f"{lang}.vtt"))
            caption_file.write_text("AUTO CAPTION", encoding="utf-8")

    dummy_module = types.SimpleNamespace(YoutubeDL=DummyDL)
    monkeypatch.setattr("docpipe.extractors.youtube.yt_dlp", dummy_module)

    extractor = YouTubeExtractor(tmp_path)
    text = extractor._download_captions(video_id)
    assert text == "AUTO CAPTION"
