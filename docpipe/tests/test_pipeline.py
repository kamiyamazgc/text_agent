import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docpipe.pipeline import process_text  # noqa: E402
from docpipe.config import Config  # noqa: E402


class DummyProcessor:
    def __init__(self, value=None):
        self.value = value

    def process(self, text):
        return text if self.value is None else self.value


def test_quality_loop_improves(monkeypatch):
    cfg = Config()
    cfg.pipeline.quality_threshold = 0.8
    cfg.pipeline.max_retries = 2
    cfg.pipeline.min_improvement = 0.0

    class DummyPre( DummyProcessor):
        def process(self, text):
            return text

    class DummyTranslator:
        def process(self, text):
            return {"text": text, "metadata": {}}

    class DummyProofreader:
        def process(self, text):
            return {"text": text, "quality_score": 1.0}

    class DummyEvaluator:
        def __init__(self):
            self.calls = 0

        def evaluate(self, text, reference=None):
            self.calls += 1
            score = 0.5 if self.calls == 1 else 0.9
            return {"quality_score": score}

    class DummyFixer:
        def process(self, text):
            return {"text": text + " fixed", "changed": True}

    res = process_text(
        "text",
        cfg,
        preprocessor=DummyPre(),
        translator=DummyTranslator(),
        proofreader=DummyProofreader(),
        evaluator=DummyEvaluator(),
        fixer=DummyFixer(),
    )
    assert res["quality_score"] >= cfg.pipeline.quality_threshold
    assert res["metadata"]["retries"] == 1


def test_quality_loop_max_retries(monkeypatch):
    cfg = Config()
    cfg.pipeline.quality_threshold = 0.9
    cfg.pipeline.max_retries = 2
    cfg.pipeline.min_improvement = 0.0

    class DummyPre(DummyProcessor):
        def process(self, text):
            return text

    class DummyTranslator:
        def process(self, text):
            return {"text": text, "metadata": {}}

    class DummyProofreader:
        def process(self, text):
            return {"text": text, "quality_score": 1.0}

    class DummyEvaluator:
        def evaluate(self, text, reference=None):
            return {"quality_score": 0.5}

    class DummyFixer:
        def process(self, text):
            return {"text": text, "changed": False}

    res = process_text(
        "text",
        cfg,
        preprocessor=DummyPre(),
        translator=DummyTranslator(),
        proofreader=DummyProofreader(),
        evaluator=DummyEvaluator(),
        fixer=DummyFixer(),
    )
    assert res["quality_score"] < cfg.pipeline.quality_threshold
    assert res["metadata"]["retries"] == cfg.pipeline.max_retries
