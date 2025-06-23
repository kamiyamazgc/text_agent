try:
    import language_tool_python as lt  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    lt = None  # type: ignore

try:
    import sacrebleu  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    sacrebleu = None  # type: ignore

try:
    from langdetect import detect as lang_detect  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    lang_detect = None  # type: ignore

try:
    from fugashi import Tagger  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Tagger = None  # type: ignore

import re
from typing import Optional, TypedDict


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
        self.tagger = Tagger() if Tagger is not None else None

    def detect_language(self, text: str) -> str:
        """Detect if text is Japanese, Chinese, or English."""
        if lang_detect is not None:
            try:
                detected = lang_detect(text)
                if detected.startswith("ja"):
                    return "ja"
                if detected.startswith("zh"):
                    return "zh"
                if detected.startswith("en"):
                    return "en"
            except Exception:  # pragma: no cover - best effort
                pass

        # Fallback regex detection
        if re.search(r"[\u3040-\u30ff]", text):
            return "ja"
        if re.search(r"[\u4e00-\u9fff]", text):
            return "zh"
        return "en"

    def grammar_error_rate(self, text: str) -> float:
        matches = self.tool.check(text)
        tokens = max(len(text.split()), 1)
        return len(matches) / tokens

    def readability_score_japanese(self, text: str) -> float:
        """Calculate readability score for Japanese text."""
        if not text.strip():
            return 1.0

        if self.tagger is not None:
            words = [tok.surface for tok in self.tagger(text)]
            if not words:
                return 1.0
            sentences = [s for s in re.split(r'[。！？]', text) if s.strip()]
            avg_word_len = sum(len(w) for w in words) / len(words)
            avg_sentence_words = len(words) / max(len(sentences), 1)
            word_len_score = 1.0 - min((avg_word_len - 2) / 6.0, 1.0)
            sent_score = 1.0 - min((avg_sentence_words - 10) / 50.0, 1.0)
            return max(0.0, min(1.0, (word_len_score + sent_score) / 2))
        
        # 文を分割（句点、感嘆符、疑問符で区切る）
        sentences = re.split(r'[。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 1.0
        
        # 文字数ベースの文の長さを計算
        total_chars = len(text)
        sentence_count = len(sentences)
        avg_sentence_length = total_chars / sentence_count
        
        # 句読点の使用頻度
        punctuation_count = len(re.findall(r'[。、！？]', text))
        punctuation_ratio = punctuation_count / max(total_chars, 1)
        
        # 漢字の使用率（適度な漢字使用は読みやすさに寄与）
        kanji_count = len(re.findall(r'[\u4e00-\u9fff]', text))
        kanji_ratio = kanji_count / max(total_chars, 1)
        
        # ひらがなの使用率
        hiragana_count = len(re.findall(r'[\u3040-\u309f]', text))
        hiragana_ratio = hiragana_count / max(total_chars, 1)
        
        # スコア計算
        # 1. 文の長さスコア（適度な長さを好む）- ペナルティを強化
        if avg_sentence_length < 20:
            length_score = 0.7  # 短すぎる文はペナルティ
        elif avg_sentence_length > 100:
            length_score = 0.3  # 長すぎる文は大幅ペナルティ
        else:
            # 20-100文字の範囲で線形補間
            length_score = 1.0 - (avg_sentence_length - 20) / 80.0 * 0.7
        
        # 2. 句読点スコア（適度な句読点使用を好む）
        punct_score = 1.0 - min(abs(punctuation_ratio - 0.1) / 0.2, 1.0)
        
        # 3. 漢字使用スコア（適度な漢字使用を好む）
        kanji_score = 1.0 - min(abs(kanji_ratio - 0.3) / 0.6, 1.0)
        
        # 4. ひらがな使用スコア（適度なひらがな使用を好む）
        hiragana_score = 1.0 - min(abs(hiragana_ratio - 0.4) / 0.8, 1.0)
        
        # 重み付き平均
        readability = (length_score * 0.4 + punct_score * 0.2 + kanji_score * 0.2 + hiragana_score * 0.2)
        return max(0.0, min(1.0, readability))

    def readability_score_english(self, text: str) -> float:
        """Calculate readability score for English text."""
        sentences = [s for s in text.split(".") if s.strip()]
        if not sentences:
            return 1.0
        words = text.split()
        avg_sentence_length = len(words) / len(sentences)
        score = 1.0 - min(avg_sentence_length / 40.0, 1.0)
        return max(0.0, score)

    def readability_score(self, text: str) -> float:
        """Calculate readability score based on detected language."""
        language = self.detect_language(text)
        if language == "ja":
            return self.readability_score_japanese(text)
        else:
            return self.readability_score_english(text)

    def bleu_score(self, text: str, reference: str) -> float:
        if sacrebleu is None:
            raise ImportError("sacrebleu is required for BLEU score")
        result = sacrebleu.corpus_bleu([text], [[reference]])
        return float(result.score)

    def evaluate(self, text: str, reference: Optional[str] = None) -> EvaluationResult:
        """Return quality metrics for given text."""
        language = self.detect_language(text)
        err_rate = self.grammar_error_rate(text)
        readability = self.readability_score(text)
        bleu = None
        if reference is not None:
            bleu = self.bleu_score(text, reference)

        # 言語に応じた品質スコア計算
        if language == "ja":
            # 日本語の場合：文法エラー率を軽視し、可読性を重視
            quality = (0.3 * (1 - err_rate) + 0.7 * readability)
        else:
            # 英語の場合：従来の計算方法
            quality = (1 - err_rate + readability) / 2

        if bleu is not None:
            quality = (quality + bleu / 100.0) / 2

        return {
            "grammar_error_rate": err_rate,
            "readability_score": readability,
            "bleu_score": bleu,
            "quality_score": quality,
        }

