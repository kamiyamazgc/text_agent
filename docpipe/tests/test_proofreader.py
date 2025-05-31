import os
import sys
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docpipe.processors.proofreader import Proofreader


def _dummy_language_tool_module():
    class DummyTool:
        def __init__(self, language: str = "ja-JP") -> None:
            pass

        def check(self, text: str):
            if "mistkae" in text:
                return [object()]
            return []

    def correct(text: str, matches) -> str:
        return text.replace("mistkae", "mistake")

    utils = types.SimpleNamespace(correct=correct)
    return types.SimpleNamespace(LanguageTool=DummyTool, utils=utils)


def test_proofread_no_errors(monkeypatch):
    monkeypatch.setattr("docpipe.processors.proofreader.lt", _dummy_language_tool_module())
    pf = Proofreader()
    result = pf.process("This is fine.")
    assert result["text"] == "This is fine."
    assert result["quality_score"] == 1.0


def test_proofread_correction(monkeypatch):
    monkeypatch.setattr("docpipe.processors.proofreader.lt", _dummy_language_tool_module())
    pf = Proofreader()
    result = pf.process("This is a mistkae.")
    assert result["text"] == "This is a mistake."
    assert result["quality_score"] < 1.0
