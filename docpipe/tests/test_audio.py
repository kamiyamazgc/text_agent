import os
import sys
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docpipe.extractors.audio import AudioExtractor


def _dummy_whisper_module():
    def load_model(model):
        def transcribe(path, language=None, verbose=False):
            return {
                "text": "hello world",
                "segments": [
                    {"start": 0.0, "end": 1.0, "text": "hello world"}
                ],
            }

        return types.SimpleNamespace(transcribe=transcribe)

    return types.SimpleNamespace(load_model=load_model)


def test_can_handle_audio(monkeypatch):
    monkeypatch.setattr("docpipe.extractors.audio.whisper", _dummy_whisper_module())
    extractor = AudioExtractor()
    assert extractor.can_handle("sample.mp3")
    assert extractor.can_handle("sample.M4A")


def test_extract_file_not_found(monkeypatch):
    monkeypatch.setattr("docpipe.extractors.audio.whisper", _dummy_whisper_module())
    extractor = AudioExtractor()
    try:
        extractor.extract("missing.mp3")
    except FileNotFoundError:
        assert True
    else:
        assert False, "FileNotFoundError not raised"


def test_extract_success(tmp_path, monkeypatch):
    monkeypatch.setattr("docpipe.extractors.audio.whisper", _dummy_whisper_module())
    fake_audio = tmp_path / "audio.mp3"
    fake_audio.write_text("dummy")
    extractor = AudioExtractor()
    result = extractor.extract(str(fake_audio))
    assert "hello world" in result["text"]
    assert result["metadata"]["source_type"] == "audio"
