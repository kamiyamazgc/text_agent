import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docpipe.pipeline import process_text  # noqa: E402
from docpipe.config import PipelineConfig  # noqa: E402


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
    cfg = PipelineConfig(quality_threshold=0.8, max_retries=3, min_improvement=0.05)
    translator = DummyTranslator()
    proofreader = DummyProofreader([0.4, 0.6, 0.9])
    evaluator = DummyEvaluator([0.4, 0.65, 0.85])
    fixer = DummyFixer()

    result = process_text("bad", cfg, translator, proofreader, evaluator, fixer)
    assert result["metadata"]["quality_score"] >= 0.8
    assert fixer.calls == 2


def test_min_improvement_breaks_loop():
    cfg = PipelineConfig(quality_threshold=0.9, max_retries=5, min_improvement=0.1)
    translator = DummyTranslator()
    proofreader = DummyProofreader([0.4, 0.45])
    evaluator = DummyEvaluator([0.4, 0.45])
    fixer = DummyFixer()

    result = process_text("bad", cfg, translator, proofreader, evaluator, fixer)
    assert result["metadata"]["retries"] == 1
    assert result["metadata"]["quality_score"] == 0.45
