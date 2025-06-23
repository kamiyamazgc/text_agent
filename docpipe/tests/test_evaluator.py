import os
import sys
import types

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


def _dummy_langdetect(lang: str):
    def detect(text: str) -> str:
        return lang

    return detect


class DummyTagger:
    def __call__(self, text: str):
        return [types.SimpleNamespace(surface=w) for w in text.split()]


def test_evaluate_no_reference(monkeypatch):
    monkeypatch.setattr(
        "docpipe.processors.evaluator.lt", _dummy_language_tool_module()
    )
    monkeypatch.setattr(
        "docpipe.processors.evaluator.sacrebleu", _dummy_sacrebleu_module()
    )
    monkeypatch.setattr("docpipe.processors.evaluator.Tagger", None)
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
    monkeypatch.setattr("docpipe.processors.evaluator.Tagger", None)
    ev = Evaluator()
    result = ev.evaluate("Translated text", reference="Reference text")
    assert result["bleu_score"] == 50.0


def test_detect_language_chinese(monkeypatch):
    monkeypatch.setattr(
        "docpipe.processors.evaluator.lt", _dummy_language_tool_module()
    )
    monkeypatch.setattr(
        "docpipe.processors.evaluator.lang_detect",
        _dummy_langdetect("zh-cn"),
    )
    monkeypatch.setattr("docpipe.processors.evaluator.Tagger", None)
    ev = Evaluator()
    assert ev.detect_language("这是中文。") == "zh"


def test_readability_japanese_with_tagger(monkeypatch):
    monkeypatch.setattr(
        "docpipe.processors.evaluator.lt", _dummy_language_tool_module()
    )
    monkeypatch.setattr(
        "docpipe.processors.evaluator.lang_detect",
        _dummy_langdetect("ja"),
    )
    monkeypatch.setattr("docpipe.processors.evaluator.Tagger", lambda: DummyTagger())
    ev = Evaluator()
    score = ev.readability_score_japanese("これは テスト です。")
    assert 0.0 <= score <= 1.0


def test_grammar_error_rate_japanese_with_tagger(monkeypatch):
    monkeypatch.setattr(
        "docpipe.processors.evaluator.lt", _dummy_language_tool_module()
    )
    monkeypatch.setattr(
        "docpipe.processors.evaluator.lang_detect",
        _dummy_langdetect("ja"),
    )
    monkeypatch.setattr("docpipe.processors.evaluator.Tagger", lambda: DummyTagger())
    ev = Evaluator()
    text = "これは error を含む 文です。"
    rate = ev.grammar_error_rate(text)
    assert rate == 1 / 4


def test_grammar_error_rate_japanese_no_tagger(monkeypatch):
    monkeypatch.setattr(
        "docpipe.processors.evaluator.lt", _dummy_language_tool_module()
    )
    monkeypatch.setattr(
        "docpipe.processors.evaluator.lang_detect",
        _dummy_langdetect("ja"),
    )
    monkeypatch.setattr("docpipe.processors.evaluator.Tagger", None)
    ev = Evaluator()
    text = "これはerrorを含む文です。"
    tokens = len([c for c in text if not c.isspace()])
    rate = ev.grammar_error_rate(text)
    assert rate == 1 / tokens


