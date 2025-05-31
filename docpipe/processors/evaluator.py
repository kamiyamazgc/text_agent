try:
    import language_tool_python as lt
except Exception:  # pragma: no cover - optional dependency
    lt = None  # type: ignore

try:
    import sacrebleu  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    sacrebleu = None  # type: ignore

from typing import Dict, Optional, TypedDict


class EvaluationResult(TypedDict):
    grammar_error_rate: float
    readability_score: float
    bleu_score: Optional[float]
    quality_score: float


class Evaluator:
    """Quality assessment using grammar check, readability, and BLEU."""

    def __init__(self, language: str = "ja-JP") -> None:
        if lt is None:
            raise ImportError("language_tool_python is required for Evaluator")
        self.tool = lt.LanguageTool(language)

    def grammar_error_rate(self, text: str) -> float:
        matches = self.tool.check(text)
        tokens = max(len(text.split()), 1)
        return len(matches) / tokens

    def readability_score(self, text: str) -> float:
        sentences = [s for s in text.split(".") if s.strip()]
        if not sentences:
            return 1.0
        words = text.split()
        avg_sentence_length = len(words) / len(sentences)
        score = 1.0 - min(avg_sentence_length / 40.0, 1.0)
        return max(0.0, score)

    def bleu_score(self, text: str, reference: str) -> float:
        if sacrebleu is None:
            raise ImportError("sacrebleu is required for BLEU score")
        result = sacrebleu.corpus_bleu([text], [[reference]])
        return float(result.score)

    def evaluate(self, text: str, reference: Optional[str] = None) -> EvaluationResult:
        """Return quality metrics for given text."""
        err_rate = self.grammar_error_rate(text)
        readability = self.readability_score(text)
        bleu = None
        if reference is not None:
            bleu = self.bleu_score(text, reference)

        quality = (1 - err_rate + readability) / 2
        if bleu is not None:
            quality = (quality + bleu / 100.0) / 2

        return {
            "grammar_error_rate": err_rate,
            "readability_score": readability,
            "bleu_score": bleu,
            "quality_score": quality,
        }

