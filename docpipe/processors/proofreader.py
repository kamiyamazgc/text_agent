try:
    import language_tool_python as lt
except Exception:  # pragma: no cover - optional dependency
    lt = None  # type: ignore

from typing import Dict, Any


class Proofreader:
    """Grammar and style proofreader using LanguageTool."""

    def __init__(self, language: str = "ja-JP") -> None:
        if lt is None:
            raise ImportError("language_tool_python is required for Proofreader")
        self.language = language
        self.tool = lt.LanguageTool(self.language)

    def proofread(self, text: str) -> str:
        """Return text corrected according to LanguageTool suggestions."""
        matches = self.tool.check(text)
        return lt.utils.correct(text, matches)

    def process(self, text: str) -> Dict[str, Any]:
        """Proofread text and return corrections with a simple quality score."""
        matches = self.tool.check(text)
        corrected = lt.utils.correct(text, matches)
        error_rate = len(matches) / max(len(text.split()), 1)
        quality_score = 1.0 - error_rate
        return {"text": corrected, "quality_score": quality_score}
