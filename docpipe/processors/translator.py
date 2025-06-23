try:
    import openai
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency
    openai = None  # type: ignore
    OpenAI = None  # type: ignore

import re
from typing import Any, Dict, Optional

from ..glossary import Glossary


class Translator:
    """Simple translator using OpenAI ChatCompletion."""

    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.7,
        prompt: str = (
            "Translate the following text to {target_lang}:\n{text}\n"
            "翻訳結果のみを返してください。"
        ),
        glossary: Optional[Glossary] = None,
    ) -> None:
        if openai is None:
            raise ImportError("openai is required for Translator")
        self.model = model
        self.temperature = temperature
        self.prompt = prompt
        self.glossary = glossary

    def detect_language(self, text: str) -> str:
        """Enhanced language detection for multiple languages."""
        # 日本語文字パターン（ひらがな、カタカナ、漢字）
        if re.search(r"[\u3040-\u30ff\u4e00-\u9fff]", text):
            return "ja"
        # 中国語文字パターン（簡体字・繁体字）
        elif re.search(r"[\u4e00-\u9fff]", text):
            return "zh"
        # 韓国語文字パターン
        elif re.search(r"[\uac00-\ud7af]", text):
            return "ko"
        # アラビア語文字パターン
        elif re.search(r"[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff\u0870-\u089f\u08b0-\u08ff\ufb50-\ufdff\ufe70-\ufeff]", text):
            return "ar"
        # ロシア語文字パターン
        elif re.search(r"[\u0400-\u04ff]", text):
            return "ru"
        # ギリシャ語文字パターン
        elif re.search(r"[\u0370-\u03ff]", text):
            return "el"
        # タイ語文字パターン
        elif re.search(r"[\u0e00-\u0e7f]", text):
            return "th"
        # ヘブライ語文字パターン
        elif re.search(r"[\u0590-\u05ff\u2000-\u206f\u20d0-\u20ff\u2100-\u214f]", text):
            return "he"
        # その他の言語は英語として扱う
        else:
            return "en"

    def translate(self, text: str, target_lang: str = "ja") -> str:
        """Translate text to the target language using ChatCompletion."""
        detected_lang = self.detect_language(text)
        if detected_lang == target_lang:
            return text
        
        # カスタムプロンプトまたはデフォルトプロンプトを使用
        default_prompt = (
            "Translate the following text to {target_lang}:\n{text}\n"
            "翻訳結果のみを返してください。"
        )
        if self.prompt == default_prompt:
            # デフォルトプロンプトの場合は詳細版を使用
            prompt = f"""以下のテキストを{target_lang}に翻訳してください。
原文の言語: {detected_lang}
翻訳先言語: {target_lang}

テキスト:
{text}

翻訳結果のみを返してください。
翻訳:"""
        else:
            # カスタムプロンプトの場合は元の処理を使用
            prompt = self.prompt.format(target_lang=target_lang, text=text)
        
        if hasattr(openai, "ChatCompletion"):
            resp = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )
        else:
            resp = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )
        if isinstance(resp, dict):
            text = resp["choices"][0]["message"]["content"].strip()
        else:
            text = resp.choices[0].message.content.strip()
        if self.glossary is not None:
            text = self.glossary.replace(text)
        return text

    def process(self, text: str) -> Dict[str, Any]:
        src_lang = self.detect_language(text)
        translated = self.translate(text, "ja")
        return {
            "text": translated,
            "metadata": {"source_language": src_lang, "model": self.model},
        }
