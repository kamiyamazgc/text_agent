import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docpipe.pipeline import process_text  # noqa: E402

from docpipe.config import Config, PipelineConfig  # noqa: E402
from docpipe.processors.spellchecker import SpellChecker


class DummyTranslator:
    def process(self, text):
        return {"text": text, "metadata": {}}


class DummyProofreader:
    def __init__(self, scores):
        self.scores = scores
        self.idx = 0

    def process(self, text):
        score = self.scores[self.idx]
        self.idx += 1
        return {"text": text, "quality_score": score}


class DummyEvaluator:
    def __init__(self, scores):
        self.scores = scores
        self.idx = 0

    def evaluate(self, text, reference=None):
        score = self.scores[self.idx]
        self.idx += 1
        return {"quality_score": score}


class DummyFixer:
    def __init__(self):
        self.calls = 0

    def process(self, text):
        self.calls += 1
        return {"text": text + f"_fix{self.calls}", "changed": True}




def test_improvement_and_threshold():
    cfg = Config()
    cfg.pipeline = PipelineConfig(quality_threshold=0.8, max_retries=3, min_improvement=0.05)
    translator = DummyTranslator()
    proofreader = DummyProofreader([0.4, 0.6, 0.9])
    evaluator = DummyEvaluator([0.4, 0.65, 0.85])
    fixer = DummyFixer()
    spellchecker = SpellChecker(quality_threshold=0.3)

    result = process_text("bad", cfg, translator, proofreader, evaluator, fixer, spellchecker)
    assert result["metadata"]["quality_score"] >= 0.8
    assert fixer.calls == 2


def test_min_improvement_breaks_loop():
    cfg = Config()
    cfg.pipeline = PipelineConfig(quality_threshold=0.9, max_retries=5, min_improvement=0.1)
    # 改善幅が設定値以下の場合にループが停止することを確認
    proofreader = DummyProofreader([0.4, 0.45, 0.44, 0.43, 0.42, 0.41])  # 徐々に悪化
    evaluator = DummyEvaluator([0.4, 0.45, 0.44, 0.43, 0.42, 0.41])  # 徐々に悪化
    translator = DummyTranslator()
    fixer = DummyFixer()
    # SpellCheckerの閾値を高く設定して、実行されないようにする
    spellchecker = SpellChecker(quality_threshold=0.3)

    result = process_text("bad", cfg, translator, proofreader, evaluator, fixer, spellchecker)
    # 2回目の評価で改善幅が0.05となり、min_improvement=0.1以下なので停止
    assert result["metadata"]["retries"] == 1
    assert result["metadata"]["quality_score"] == 0.45


def test_long_text_chunking():
    cfg = Config()
    cfg.pipeline = PipelineConfig()

    class CTranslator:
        def __init__(self):
            self.calls = 0

        def process(self, text):
            self.calls += 1
            return {"text": text, "metadata": {}}

    class CProof:
        def process(self, text):
            return {"text": text, "quality_score": 1.0}

    class CEval:
        def evaluate(self, text, reference=None):
            return {"quality_score": 1.0}

    translator = CTranslator()
    proofreader = CProof()
    evaluator = CEval()
    fixer = DummyFixer()
    spellchecker = SpellChecker(quality_threshold=0.3)

    long_text = " ".join([f"w{i}" for i in range(25)])
    result = process_text(
        long_text,
        cfg,
        translator,
        proofreader,
        evaluator,
        fixer,
        spellchecker,
        max_tokens=10,
    )

    assert translator.calls == 5  # SpellChecker分も含めて5回
    assert result["text"].strip() == long_text
    assert len(result["metadata"]["chunks"]) == 5


def test_skip_proofreader_when_disabled():
    cfg = Config()
    cfg.pipeline = PipelineConfig()
    cfg.proofreader.enabled = False

    translator = DummyTranslator()
    proofreader = DummyProofreader([0.4])
    evaluator = DummyEvaluator([0.9])
    fixer = DummyFixer()
    spellchecker = SpellChecker(quality_threshold=0.3)

    result = process_text("text", cfg, translator, proofreader, evaluator, fixer, spellchecker)

    assert proofreader.idx == 0
    assert result["metadata"]["quality_score"] == 0.9


def test_grammar_error_threshold_penalty():
    cfg = Config()
    cfg.pipeline = PipelineConfig(max_retries=0, language_tool_threshold=0.02)

    translator = DummyTranslator()
    proofreader = DummyProofreader([0.9])

    class Eval:
        def evaluate(self, text, reference=None):
            return {
                "grammar_error_rate": 0.05,
                "bleu_score": None,
                "quality_score": 0.95,
            }

    evaluator = Eval()
    fixer = DummyFixer()
    spellchecker = SpellChecker(quality_threshold=0.3)

    result = process_text("text", cfg, translator, proofreader, evaluator, fixer, spellchecker)
    assert result["metadata"]["quality_score"] == 0.0


def test_bleu_threshold_penalty():
    cfg = Config()
    cfg.pipeline = PipelineConfig(max_retries=0, bleu_threshold=50.0)

    translator = DummyTranslator()
    proofreader = DummyProofreader([0.9])

    class Eval:
        def evaluate(self, text, reference=None):
            return {
                "grammar_error_rate": 0.0,
                "bleu_score": 10.0,
                "quality_score": 0.95,
            }

    evaluator = Eval()
    fixer = DummyFixer()
    spellchecker = SpellChecker(quality_threshold=0.3)

    result = process_text("text", cfg, translator, proofreader, evaluator, fixer, spellchecker)
    assert result["metadata"]["quality_score"] == 0.0
