try:
    import openai
except Exception:  # pragma: no cover - optional dependency
    openai = None  # type: ignore

import re
from typing import Any, Dict


class Translator:
    """Simple translator using OpenAI ChatCompletion."""

    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.7,
        prompt: str = "Translate the following text to {target_lang}:\n{text}",
    ) -> None:
        if openai is None:
            raise ImportError("openai is required for Translator")
        self.model = model
        self.temperature = temperature
        self.prompt = prompt

    def detect_language(self, text: str) -> str:
        """Very naive language detection."""
        if re.search("[\u3040-\u30ff\u4e00-\u9fff]", text):
            return "ja"
        return "en"

    def translate(self, text: str, target_lang: str = "ja") -> str:
        """Translate text to the target language using ChatCompletion."""
        if target_lang == self.detect_language(text):
            return text
        prompt = self.prompt.format(target_lang=target_lang, text=text)
        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
        )
        return resp["choices"][0]["message"]["content"].strip()

    def process(self, text: str) -> Dict[str, Any]:
        src_lang = self.detect_language(text)
        translated = self.translate(text, "ja")
        return {
            "text": translated,
            "metadata": {"source_language": src_lang, "model": self.model},
        }
