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
        # Join lines that are not terminated by punctuation or part of a blank
        # line. This merges lines within a single paragraph while leaving
        # paragraph breaks intact.
        text = re.sub(r"(?<![.!?。？！：:\n])\n(?!\n)", " ", text)

        # Ensure that a single newline following punctuation becomes a blank
        # line to separate paragraphs.
        text = re.sub(r"(?<=[.!?。？！：:])\n(?!\n)", "\n\n", text)

        # Collapse runs of blank lines down to a single blank line for
        # consistency.
        text = re.sub(r"\n{2,}", "\n\n", text)

        return text.strip()

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
