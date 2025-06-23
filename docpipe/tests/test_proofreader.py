import os
import sys
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docpipe.processors.proofreader import Proofreader  # noqa: E402
from docpipe.glossary import Glossary


def _dummy_openai_module(result: str = ""):

    class DummyChatCompletion:
        @staticmethod
        def create(model, messages, temperature=0.0):
            return {"choices": [{"message": {"content": result}}]}

    return types.SimpleNamespace(ChatCompletion=DummyChatCompletion)


def _capture_openai_module(store: dict):
    class DummyChatCompletion:
        @staticmethod
        def create(model, messages, temperature=0.0):
            store["prompt"] = messages[0]["content"]
            return {"choices": [{"message": {"content": "ok"}}]}

    return types.SimpleNamespace(ChatCompletion=DummyChatCompletion)


def test_proofread_no_errors(monkeypatch):
    monkeypatch.setattr(
        "docpipe.processors.proofreader.openai", _dummy_openai_module("This is fine.")
    )
    pf = Proofreader()
    result = pf.process("This is fine.")
    assert result["text"] == "This is fine."
    assert result["quality_score"] == 1.0


def test_proofread_correction(monkeypatch):
    monkeypatch.setattr(
        "docpipe.processors.proofreader.openai",
        _dummy_openai_module("This is a mistake."),
    )
    pf = Proofreader()
    result = pf.process("This is a mistkae.")
    assert result["text"] == "This is a mistake."
    assert result["quality_score"] < 1.0


def test_custom_prompt(monkeypatch):
    store = {}
    monkeypatch.setattr(
        "docpipe.processors.proofreader.openai",
        _capture_openai_module(store),
    )
    pf = Proofreader(prompt="P {style}")
    pf.proofread("x")
    assert store["prompt"] == "P general"


def test_proofreader_applies_glossary(monkeypatch, tmp_path):
    gfile = tmp_path / "gl.csv"
    gfile.write_text("ja,en\nマイクロソフト,Microsoft\n", encoding="utf-8")
    glossary = Glossary(str(gfile))
    monkeypatch.setattr(
        "docpipe.processors.proofreader.openai", _dummy_openai_module("マイクロソフト")
    )
    pf = Proofreader(glossary=glossary)
    result = pf.process("Microsoft")
    assert "マイクロソフト" in result["text"]
