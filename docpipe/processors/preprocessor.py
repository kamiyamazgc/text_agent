import re
from typing import Dict


class Preprocessor:
    """Text normalization and cleanup processor."""

    OCR_CORRECTIONS: Dict[str, str] = {
        "ﬁ": "fi",
        "ﬂ": "fl",
        "’": "'",
        "“": '"',
        "”": '"',
        "—": "-",
        "–": "-",
    }

    def correct_ocr_errors(self, text: str) -> str:
        """Apply common OCR corrections."""
        for wrong, correct in self.OCR_CORRECTIONS.items():
            text = text.replace(wrong, correct)
        return text

    def restore_line_breaks(self, text: str) -> str:
        """Restore line breaks by merging lines inside paragraphs."""
        lines = text.splitlines()
        restored: list[str] = []
        punct = (".", "?", "!", "。", "？", "！", "：", ":")
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if restored and restored[-1] != "":
                    restored.append("")
                continue

            if (
                restored
                and restored[-1]
                and not restored[-1].endswith(punct)
            ):
                restored[-1] += " " + stripped
            else:
                if (
                    restored
                    and restored[-1]
                    and restored[-1].endswith(punct)
                    and (len(restored) == 1 or restored[-2] != "")
                ):
                    restored.append("")
                restored.append(stripped)
        return "\n".join(restored)

    def standardize_format(self, text: str) -> str:
        """Standardize newlines and spacing."""
        text = text.replace("\r\n", "\n")
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        lines = [line.rstrip() for line in text.splitlines()]
        return "\n".join(lines).strip()

    def process(self, text: str) -> str:
        """Run all preprocessing steps."""
        text = self.correct_ocr_errors(text)
        text = self.restore_line_breaks(text)
        text = self.standardize_format(text)
        return text
