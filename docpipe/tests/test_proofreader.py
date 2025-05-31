import os
import sys
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docpipe.processors.proofreader import Proofreader  # noqa: E402


def _dummy_openai_module(result: str = "修正後"):
    class DummyChatCompletion:
        @staticmethod
        def create(model, messages, temperature=0.0):
            return {"choices": [{"message": {"content": result}}]}

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
