try:
    import openai
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency
    openai = None  # type: ignore
    OpenAI = None  # type: ignore

from typing import Dict, Any, Optional


class Proofreader:
    """Grammar and style proofreader using OpenAI ChatCompletion."""

    def __init__(
        self,
        model: str = "gpt-4o",
        style: str = "general",
        temperature: float = 0.0,
        prompt: str = (
            "Proofread the following text. Fix grammar, style, and readability "
            "issues in {style} style. 文の意味を変えないこと。未知の用語はそのまま残すこと。"
            "結果だけを出力してください。"
        ),
    ) -> None:
        if openai is None:
            raise ImportError("openai is required for Proofreader")
        self.model = model
        self.style = style
        self.temperature = temperature
        self.prompt = prompt

    def proofread(
        self,
        text: str,
        error_rate: Optional[float] = None,
        readability: Optional[float] = None,
    ) -> str:
        """Return text corrected by ChatGPT."""
        prompt = self.prompt.format(style=self.style)
        metrics: list[str] = []
        if error_rate is not None:
            metrics.append(f"grammar error rate {error_rate:.2%}")
        if readability is not None:
            metrics.append(f"readability score {readability:.2f}")
        if metrics:
            prompt += " Current metrics: " + ", ".join(metrics) + "."
        if hasattr(openai, "ChatCompletion"):
            resp = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text},
                ],
                temperature=self.temperature,
            )
        else:
            resp = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text},
                ],
                temperature=self.temperature,
            )
        if isinstance(resp, dict):
            return resp["choices"][0]["message"]["content"].strip()
        return resp.choices[0].message.content.strip()

    def process(
        self,
        text: str,
        error_rate: Optional[float] = None,
        readability: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Proofread text and return corrections with a simple quality score."""
        corrected = self.proofread(text, error_rate=error_rate, readability=readability)
        quality_score = 1.0 if corrected == text else 0.95
        return {"text": corrected, "quality_score": quality_score}
