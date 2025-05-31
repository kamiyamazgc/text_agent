try:
    import openai
except Exception:  # pragma: no cover - optional dependency
    openai = None  # type: ignore

from typing import Dict, Any


class Proofreader:
    """Grammar and style proofreader using OpenAI ChatCompletion."""

    def __init__(
        self, model: str = "gpt-4o", temperature: float = 0.0, style: str = "general"
    ) -> None:
        if openai is None:
            raise ImportError("openai is required for Proofreader")
        self.model = model
        self.temperature = temperature
        self.style = style

    def proofread(self, text: str) -> str:
        """Return text corrected by ChatCompletion."""
        system_prompt = "You are a meticulous Japanese proofreader."
        if self.style != "general":
            system_prompt += f" Use {self.style} style."
        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=self.temperature,
        )
        return resp["choices"][0]["message"]["content"].strip()

    def process(self, text: str) -> Dict[str, Any]:
        """Proofread text and return corrections with a simple quality score."""
        corrected = self.proofread(text)
        quality_score = 1.0 if corrected == text else 0.95
        return {"text": corrected, "quality_score": quality_score}
