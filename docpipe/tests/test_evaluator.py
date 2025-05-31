import os
import sys
import types
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docpipe.processors.evaluator import Evaluator  # noqa: E402


def _dummy_language_tool_module():
    class DummyTool:
        def __init__(self, language: str = "ja-JP") -> None:
            pass

        def check(self, text: str):
            return [object()] if "error" in text else []

    return types.SimpleNamespace(LanguageTool=DummyTool)


def _dummy_sacrebleu_module(score: float = 100.0):
    class DummyResult:
        def __init__(self, score: float) -> None:
            self.score = score

    def corpus_bleu(hypotheses, references):
        return DummyResult(score)

    return types.SimpleNamespace(corpus_bleu=corpus_bleu)


def test_evaluate_no_reference(monkeypatch):
    monkeypatch.setattr(
        "docpipe.processors.evaluator.lt", _dummy_language_tool_module()
    )
    monkeypatch.setattr(
        "docpipe.processors.evaluator.sacrebleu", _dummy_sacrebleu_module()
    )
    ev = Evaluator()
    result = ev.evaluate("This text is fine.")
    assert result["grammar_error_rate"] == 0.0
    assert result["bleu_score"] is None


def test_evaluate_with_reference(monkeypatch):
    monkeypatch.setattr(
        "docpipe.processors.evaluator.lt", _dummy_language_tool_module()
    )
    monkeypatch.setattr(
        "docpipe.processors.evaluator.sacrebleu", _dummy_sacrebleu_module(50.0)
    )
    ev = Evaluator()
    result = ev.evaluate("Translated text", reference="Reference text")
    assert result["bleu_score"] == 50.0


