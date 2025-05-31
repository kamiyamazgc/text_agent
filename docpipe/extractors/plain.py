from pathlib import Path
from typing import Any, Dict, Tuple

from .base import BaseExtractor


class PlainTextExtractor(BaseExtractor):
    """Extractor for plain text and Markdown files."""

    SUPPORTED_EXTENSIONS: Tuple[str, ...] = (".txt", ".md")

    def can_handle(self, source: str) -> bool:
        """Check if the source is a plain text or Markdown file."""
        return source.lower().endswith(self.SUPPORTED_EXTENSIONS)

    def extract(self, source: str, **kwargs: Any) -> Dict[str, Any]:
        """Read the file and return its text."""
        file_path = Path(source)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {source}")

        text = file_path.read_text(encoding="utf-8")
        metadata = {
            "source_type": "plain",
            "file_name": file_path.name,
        }
        return {"text": text, "metadata": metadata}
