"""Marker PDF extractor for high-quality text extraction."""

from pathlib import Path
from typing import Tuple, List, Dict, Any
import marker  # type: ignore

def to_text_with_layout(pdf_path: Path) -> Tuple[str, List[Dict[str, Any]]]:
    """Extract text with layout information using marker-pdf."""
    return marker.to_text_with_layout(pdf_path)
