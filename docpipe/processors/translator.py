try:
    import openai
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency
    openai = None  # type: ignore
    OpenAI = None  # type: ignore

import re
from typing import Any, Dict, Optional

from ..glossary import Glossary
from ..utils.markdown_utils import (
    is_markdown_file, 
    extract_critical_markdown_blocks,
    restore_critical_markdown_blocks
)


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

    def translate(self, text: str, source_lang: str = "en", target_lang: str = "ja") -> str:
        """Translate text from source language to target language."""
        if not text.strip():
            return text
        
        # Markdownファイルの場合は見出し・表・画像を絶対保護
        critical_blocks = {}
        if is_markdown_file(text):
            print("DEBUG: Translator - Markdown file detected")
            # 見出し・表・画像を絶対保護
            text, critical_blocks = extract_critical_markdown_blocks(text)
            print(f"DEBUG: Translator - Protected {len(critical_blocks)} critical blocks (headers, tables, images)")
        
        # 通常の翻訳処理
        if is_markdown_file(text):
            # Markdown対応翻訳
            result = self._translate_with_markdown_preservation(text, target_lang, {})
        else:
            # 通常翻訳
            result = self._translate_text(text, source_lang, target_lang)
        
        # 見出し・表・画像を必ず復元
        if critical_blocks:
            print("DEBUG: Translator - Restoring critical markdown blocks (headers, tables, images)")
            result = restore_critical_markdown_blocks(result, critical_blocks)
            print(f"DEBUG: Translator - Restored {len(critical_blocks)} critical blocks")
        
        return result

    def translate_markdown(self, text: str, target_lang: str = "ja") -> str:
        """Translate Markdown text while preserving formatting."""
        # Markdownブロックを抽出して保護（重要な要素のみ）
        processed_text, markdown_blocks = extract_critical_markdown_blocks(text)
        
        # テキストコンテンツのみを翻訳（Markdown構造保持の指示付き）
        translated_text = self._translate_with_markdown_preservation(processed_text, target_lang, markdown_blocks)
        
        # Markdownブロックを復元
        translated_text = restore_critical_markdown_blocks(translated_text, markdown_blocks)
        
        return translated_text
    
    def _translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate plain text from source language to target language."""
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
        
        # 新APIで統一
        client = OpenAI()
        resp = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
        )
        text = resp.choices[0].message.content.strip()
        if self.glossary is not None:
            text = self.glossary.replace(text)
        return text

    def _translate_with_markdown_preservation(self, text: str, target_lang: str, markdown_blocks: dict) -> str:
        """Translate text while preserving markdown placeholders."""
        print(f"=== Translator: 入力テキスト（最初の100文字） ===")
        print(repr(text[:100]))
        print(f"=== Translator: 入力テキスト（全体の長さ: {len(text)}文字） ===")
        
        # 重要なMarkdownプレースホルダーを検出（見出し・表・画像のみ）
        critical_placeholders = re.findall(r'__CRITICAL_[A-Z_]+_\d+__', text)
        image_placeholders = [p for p in critical_placeholders if 'IMAGE' in p]
        table_placeholders = [p for p in critical_placeholders if 'TABLE' in p]
        header_placeholders = [p for p in critical_placeholders if 'HEADER' in p]
        
        # 翻訳プロンプトにMarkdown保持の指示を追加
        prompt = f"""Translate into {target_lang}. Don't modify or delete any Markdown format. Answer the result only:

{text}"""
        
        print(f"=== Translator: LLM送信前テキスト（最初の100文字） ===")
        print(repr(text[:100]))
        print(f"=== Translator: プロンプト（最初の200文字） ===")
        print(repr(prompt[:200]))
        
        # 新APIで統一
        client = OpenAI()
        resp = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
        )
        translated = resp.choices[0].message.content.strip()
        
        print(f"=== Translator: LLM返却テキスト（最初の100文字） ===")
        print(repr(translated[:100]))
        print(f"=== Translator: LLM返却テキスト（全体の長さ: {len(translated)}文字） ===")
        
        if self.glossary is not None:
            translated = self.glossary.replace(translated)
        return translated

    def process(self, text: str) -> Dict[str, Any]:
        src_lang = self.detect_language(text)
        
        # Markdownファイルの場合は特別な処理
        if is_markdown_file(text):
            translated = self.translate_markdown(text, "ja")
        else:
            translated = self.translate(text, "en", "ja")
            
        return {
            "text": translated,
            "metadata": {"source_language": src_lang, "model": self.model},
        }
