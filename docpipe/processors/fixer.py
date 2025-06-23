import re
from typing import Any, Dict

class Fixer:
    """Enhanced error correction agent with text structure improvements."""

    def remove_duplicate_lines(self, text: str) -> str:
        lines = text.splitlines()
        cleaned: list[str] = []
        for line in lines:
            if not cleaned or line != cleaned[-1]:
                cleaned.append(line)
        return "\n".join(cleaned)

    def balance_parentheses(self, text: str) -> str:
        diff = text.count("(") - text.count(")")
        if diff > 0:
            text += ")" * diff
        elif diff < 0:
            text = "(" * (-diff) + text
        return text

    def fix_common_typos(self, text: str) -> str:
        corrections = {
            r"\bteh\b": "the",
            r"\brecieve\b": "receive",
        }
        for pattern, repl in corrections.items():
            text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
        text = re.sub(r" {2,}", " ", text)
        return text

    def fix_speech_recognition_errors(self, text: str) -> str:
        """Fix common speech recognition errors in Japanese text."""
        # 音声認識でよく発生する誤認識パターン
        speech_corrections = {
            # 専門用語の誤認識
            r"アイロン": "アライアンス",
            r"アイロンと": "アライアンスと",
            r"アイロンの": "アライアンスの",
            r"アイロンは": "アライアンスは",
            
            # 固有名詞の誤認識
            r"Win Hello": "Windows Hello",
            r"Win EOS": "Windows EOS",
            r"Win10": "Windows 10",
            r"Win 10": "Windows 10",
            r"Ryzen AI5": "Ryzen 5",
            r"Ryzen AI 5": "Ryzen 5",
            r"Ryzen AI7": "Ryzen 7",
            r"Ryzen AI 7": "Ryzen 7",
            r"Ryzen AI9": "Ryzen 9",
            r"Ryzen AI 9": "Ryzen 9",
            
            # 一般的な音声認識エラー
            r"ココパイロット": "コパイロット",  # 重複修正
            r"パイロットプラス": "コパイロットプラス",
            r"パイロット": "コパイロット",
            
            # 音声認識の不完全な単語
            r"\bす\b": "",  # 単独の「す」
            r"\br\b": "",  # 単独の「r」
            r"\bned\b": "",  # 不完全な単語
            r"\bOops\b": "",  # 音声認識エラー
            r"\bs\b": "",  # 単独の「s」
            r"\bgotten\b": "",  # 不完全な単語
            
            # 句読点の誤認識
            r"、\s*、": "、",
            r"。\s*。": "。",
            r"！\s*！": "！",
            r"？\s*？": "？",
            
            # 空白の誤認識
            r"（削除）": "",
            r"\(削除\)": "",
        }
        
        for pattern, repl in speech_corrections.items():
            text = re.sub(pattern, repl, text)
        
        return text

    def remove_speech_artifacts(self, text: str) -> str:
        """Remove speech recognition artifacts and noise."""
        # 音声認識のノイズやアーティファクトを削除
        artifacts_patterns = [
            r"\[[0-9]+\.[0-9]+-[0-9]+\.[0-9]+\]\s*speaker_[12]:\s*$",  # 空のタイムスタンプ行
            r"^speaker_[12]:\s*$",  # 空の話者行
            r"^\[[0-9]+\.[0-9]+-[0-9]+\.[0-9]+\]\s*$",  # タイムスタンプのみの行
            r"^[0-9]+\.[0-9]+-[0-9]+\.[0-9]+\s*$",  # タイムスタンプのみの行（括弧なし）
        ]
        
        lines = text.splitlines()
        cleaned_lines = []
        
        for line in lines:
            # アーティファクトパターンにマッチしない行のみ保持
            is_artifact = False
            for pattern in artifacts_patterns:
                if re.match(pattern, line.strip()):
                    is_artifact = True
                    break
            
            if not is_artifact:
                cleaned_lines.append(line)
        
        return "\n".join(cleaned_lines)

    def normalize_speech_text(self, text: str) -> str:
        """Normalize speech recognition text for better readability."""
        # 音声認識テキストの正規化
        lines = text.splitlines()
        normalized_lines = []
        
        for line in lines:
            if line.strip() == "":
                normalized_lines.append("")
                continue
            
            # タイムスタンプと話者情報を削除
            # [0:00-12:02] speaker_2: の形式を削除
            line = re.sub(r"^\[[0-9]+\.[0-9]+-[0-9]+\.[0-9]+\]\s*speaker_[12]:\s*", "", line)
            
            # 行が空でない場合は追加
            if line.strip():
                normalized_lines.append(line.strip())
        
        # 連続する空行を削除
        result_lines = []
        prev_empty = False
        for line in normalized_lines:
            if line == "":
                if not prev_empty:
                    result_lines.append("")
                prev_empty = True
            else:
                result_lines.append(line)
                prev_empty = False
        
        # 最後の空行を削除
        while result_lines and result_lines[-1] == "":
            result_lines.pop()
        
        return "\n".join(result_lines)

    def normalize_punctuation(self, text: str) -> str:
        """Normalize punctuation marks for better readability."""
        lines = text.splitlines()
        result_lines = []
        
        for line in lines:
            if line.strip() == "":
                result_lines.append("")
            else:
                # 行内の句読点正規化
                normalized_line = line
                # 全角スペースを半角に統一
                normalized_line = re.sub(r"\u3000", " ", normalized_line)
                
                # 英語部分の句読点を半角に統一（日本語部分は保持）
                normalized_line = re.sub(r"([a-zA-Z])\s*、\s*([a-zA-Z])", r"\1, \2", normalized_line)
                normalized_line = re.sub(r"([a-zA-Z])\s*．\s*([a-zA-Z])", r"\1. \2", normalized_line)
                normalized_line = re.sub(r"([a-zA-Z])\s*！\s*([a-zA-Z])", r"\1! \2", normalized_line)
                normalized_line = re.sub(r"([a-zA-Z])\s*？\s*([a-zA-Z])", r"\1? \2", normalized_line)
                
                # 連続する句読点を整理（日本語・英語両方）
                normalized_line = re.sub(r"[,，]{2,}", "、", normalized_line)
                normalized_line = re.sub(r"[.．]{2,}", "。", normalized_line)
                normalized_line = re.sub(r"[!！]{2,}", "！", normalized_line)
                normalized_line = re.sub(r"[?？]{2,}", "？", normalized_line)
                
                # 括弧の前後の空白調整
                normalized_line = re.sub(r"\s*\(\s*", " (", normalized_line)
                normalized_line = re.sub(r"\s*\)\s*", ") ", normalized_line)
                normalized_line = re.sub(r"\s*\[\s*", " [", normalized_line)
                normalized_line = re.sub(r"\s*\]\s*", "] ", normalized_line)
                
                result_lines.append(normalized_line)
        
        return "\n".join(result_lines)

    def normalize_line_breaks(self, text: str) -> str:
        """Normalize line breaks and spacing for better structure."""
        # 行頭・行末の空白削除
        lines = text.splitlines()
        cleaned_lines = [line.strip() for line in lines]
        
        # 空行を削除して2行以上の連続改行を2行に統一
        result_lines = []
        prev_empty = False
        for line in cleaned_lines:
            if line == "":
                if not prev_empty:
                    result_lines.append("")
                prev_empty = True
            else:
                result_lines.append(line)
                prev_empty = False
        
        # 最後の空行を削除
        while result_lines and result_lines[-1] == "":
            result_lines.pop()
        
        return "\n".join(result_lines)

    def _is_python_code(self, text: str) -> bool:
        """Check if the text appears to be Python source code."""
        # Pythonコードの特徴を検出
        python_indicators = [
            r'import\s+\w+',
            r'from\s+\w+\s+import',
            r'def\s+\w+\s*\(',
            r'class\s+\w+',
            r'#\s*SPDX-',
            r'__all__\s*=',
        ]
        
        text_lower = text.lower()
        for pattern in python_indicators:
            if re.search(pattern, text_lower):
                return True
        
        return False

    def adjust_spacing(self, text: str) -> str:
        """Adjust spacing for better readability."""
        # Pythonコードの場合は特別な処理
        if self._is_python_code(text):
            return self._adjust_spacing_python(text)
        
        lines = text.splitlines()
        result_lines = []
        
        for line in lines:
            if line.strip() == "":
                result_lines.append("")
            else:
                # 行内の空白調整
                adjusted_line = line
                # 連続する空白を1つに
                adjusted_line = re.sub(r" {2,}", " ", adjusted_line)
                # 句読点の前の空白を削除
                adjusted_line = re.sub(r"\s+([,.!?;:、。！？：；])", r"\1", adjusted_line)
                # 英語句読点の後の空白を1つに統一
                adjusted_line = re.sub(r"([,.!?;:])\s*", r"\1 ", adjusted_line)
                # 日本語句読点の後の空白を削除（行末は除く）
                adjusted_line = re.sub(r"([、。！？：；])\s+(?!$)", r"\1", adjusted_line)
                result_lines.append(adjusted_line)
        
        return "\n".join(result_lines)

    def _adjust_spacing_python(self, text: str) -> str:
        """Adjust spacing for Python source code while preserving syntax."""
        lines = text.splitlines()
        result_lines = []
        
        for line in lines:
            if line.strip() == "":
                result_lines.append("")
            else:
                # Pythonコードの場合は最小限の調整のみ
                adjusted_line = line
                # 連続する空白を1つに（ただしインデントは保持）
                adjusted_line = re.sub(r"(?<!^) {2,}", " ", adjusted_line)
                # 行末の空白を削除
                adjusted_line = adjusted_line.rstrip()
                result_lines.append(adjusted_line)
        
        return "\n".join(result_lines)

    def improve_structure(self, text: str) -> str:
        """Improve document structure with proper line breaks after headings."""
        lines = text.splitlines()
        result_lines = []
        
        for i, line in enumerate(lines):
            result_lines.append(line)
            
            # 見出しの後に改行を追加
            if self._is_heading(line):
                # 次の行が空でない場合は空行を追加
                if i + 1 < len(lines) and lines[i + 1].strip() != "":
                    result_lines.append("")
        
        return "\n".join(result_lines)
    
    def _is_heading(self, line: str) -> bool:
        """Check if a line is a heading."""
        line = line.strip()

        # 数字を含む行は見出しとみなさない
        if re.search(r"\d", line):
            return False
        
        # 見出しのパターンを検出
        heading_patterns = [
            r"^#{1,6}\s+",  # Markdown形式
            r"^[A-Z][A-Z\s]+$",  # 大文字のみの行
            r"^[一二三四五六七八九十]+[、．]",  # 日本語の番号付き見出し
            r"^[0-9]+[、．]",  # 数字の番号付き見出し
            r"^[A-Z][^.!?]*$",  # 文頭が大文字で文末に句読点がない行
            r"^[あ-んア-ン一-龯]+[：:]",  # 日本語見出し（：で終わる）
            r"^第[一二三四五六七八九十\d]+[章節]",  # 第X章、第X節
            r"^[一二三四五六七八九十\d]+[、．]\s*[あ-んア-ン一-龯]+",  # 番号付き見出し
            r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$",  # Title Case見出し
            r"^[（(][一二三四五六七八九十\d]+[）)]",  # （1）（一）形式
            r"^[①②③④⑤⑥⑦⑧⑨⑩]",  # 丸数字
            r"^[A-Z][A-Z\s]+[：:]",  # 英語見出し（：で終わる）
            r"^[あ-んア-ン一-龯]{2,}[（(][一二三四五六七八九十\d]+[）)]",  # 日本語見出し（番号付き）
            r"^[あ-んア-ン一-龯]{2,}\s*[（(][一二三四五六七八九十\d]+[）)]",  # 日本語見出し（番号付き、空白あり）
        ]
        
        for pattern in heading_patterns:
            if re.match(pattern, line):
                return True
        
        return False

    def process(self, text: str) -> Dict[str, Any]:
        original = text
        
        # Pythonコードの場合は特別な処理
        if self._is_python_code(text):
            return self._process_python_code(text)
        
        # 音声認識テキストの場合は特別な処理
        if self._is_speech_text(text):
            return self._process_speech_text(text)
        
        # 処理順序を最適化
        # 1. 基本的な修正
        text = self.remove_duplicate_lines(text)
        text = self.balance_parentheses(text)
        text = self.fix_common_typos(text)
        
        # 2. 句読点の正規化（空白調整の前に実行）
        text = self.normalize_punctuation(text)
        
        # 3. 空白・改行の正規化
        text = self.normalize_line_breaks(text)
        text = self.adjust_spacing(text)
        
        # 4. 構造の改善（最後に実行して他の処理で上書きされないようにする）
        text = self.improve_structure(text)
        
        changed = text != original
        return {"text": text, "changed": changed}

    def _is_speech_text(self, text: str) -> bool:
        """Check if the text appears to be speech recognition output."""
        # 音声認識テキストの特徴を検出
        speech_indicators = [
            r"\[[0-9]+\.[0-9]+-[0-9]+\.[0-9]+\]\s*speaker_[12]:",  # タイムスタンプと話者
            r"speaker_[12]:",  # 話者情報
            r"\[[0-9]+\.[0-9]+-[0-9]+\.[0-9]+\]",  # タイムスタンプ
        ]
        
        for pattern in speech_indicators:
            if re.search(pattern, text):
                return True
        
        return False

    def _process_speech_text(self, text: str) -> Dict[str, Any]:
        """Process speech recognition text with specialized corrections."""
        original = text
        
        # 音声認識テキストの専用処理
        # 1. 音声認識エラーの修正
        text = self.fix_speech_recognition_errors(text)
        
        # 2. アーティファクトの削除
        text = self.remove_speech_artifacts(text)
        
        # 3. テキストの正規化（タイムスタンプ削除など）
        text = self.normalize_speech_text(text)
        
        # 4. 基本的な修正
        text = self.remove_duplicate_lines(text)
        text = self.balance_parentheses(text)
        text = self.fix_common_typos(text)
        
        # 5. 句読点の正規化
        text = self.normalize_punctuation(text)
        
        # 6. 空白・改行の正規化
        text = self.normalize_line_breaks(text)
        text = self.adjust_spacing(text)
        
        # 7. 構造の改善
        text = self.improve_structure(text)
        
        changed = text != original
        return {"text": text, "changed": changed}

    def _process_python_code(self, text: str) -> Dict[str, Any]:
        """Process Python source code with minimal changes to preserve syntax."""
        original = text
        
        # Pythonコードの場合は最小限の処理のみ
        # 1. 改行の正規化（インデントは保持）
        text = self._normalize_line_breaks_python(text)
        
        # 2. 行末の空白削除のみ
        lines = text.splitlines()
        result_lines = []
        for line in lines:
            if line.strip() == "":
                result_lines.append("")
            else:
                # 行末の空白のみ削除（インデントは保持）
                result_lines.append(line.rstrip())
        
        text = "\n".join(result_lines)
        
        changed = text != original
        return {"text": text, "changed": changed}

    def _normalize_line_breaks_python(self, text: str) -> str:
        """Normalize line breaks for Python code while preserving indentation."""
        lines = text.splitlines()
        result_lines = []
        
        for line in lines:
            # 空行の場合はそのまま追加
            if line.strip() == "":
                result_lines.append("")
            else:
                # インデントを保持して行末の空白のみ削除
                result_lines.append(line.rstrip())
        
        # 最後の空行を削除
        while result_lines and result_lines[-1] == "":
            result_lines.pop()
        
        return "\n".join(result_lines)

