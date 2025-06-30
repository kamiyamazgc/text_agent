import re
from typing import Dict
from ..utils.markdown_utils import (
    is_markdown_file, 
    extract_critical_markdown_blocks, 
    restore_critical_markdown_blocks
)


class Preprocessor:
    """Text normalization and cleanup processor."""

    OCR_CORRECTIONS: Dict[str, str] = {
        "ﬁ": "fi",
        "ﬂ": "fl",
        "'": "'",
        """: '"',
        """: '"',
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
        # Check if this is a Markdown file
        if is_markdown_file(text):
            # Extract Markdown blocks to protect them
            processed_text, markdown_blocks = extract_critical_markdown_blocks(text)
            
            # Apply preprocessing to the text content only
            processed_text = self.correct_ocr_errors(processed_text)
            processed_text = self.restore_line_breaks(processed_text)
            processed_text = self.standardize_format(processed_text)
            
            # Restore Markdown blocks
            processed_text = restore_critical_markdown_blocks(processed_text, markdown_blocks)
            
            return processed_text
        else:
            # Original processing for non-Markdown files
            text = self.correct_ocr_errors(text)
            text = self.restore_line_breaks(text)
            text = self.standardize_format(text)
            return text
