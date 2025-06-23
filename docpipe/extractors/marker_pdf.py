from pathlib import Path
from typing import Tuple, List

try:
    import marker_pdf  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    marker_pdf = None  # type: ignore


def to_text_with_layout(pdf_path: str) -> Tuple[str, List[str]]:
    """Extract text and layout information using marker-pdf."""
    if marker_pdf is None:
        raise ImportError("marker-pdf is required for PDF extraction")
    return marker_pdf.to_text_with_layout(Path(pdf_path))
