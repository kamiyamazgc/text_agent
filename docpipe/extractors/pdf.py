from pathlib import Path
from typing import Any, Dict

try:
    import marker_pdf  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    marker_pdf = None  # type: ignore

from .base import BaseExtractor


class PDFExtractor(BaseExtractor):
    """Extractor for digital PDFs using marker-pdf"""

    def can_handle(self, source: str) -> bool:
        """Check if the source is a PDF file"""
        return source.lower().endswith(".pdf")

    def extract(self, source: str, **kwargs: Any) -> Dict[str, Any]:
        """Extract text from a digital PDF with optional layout information."""
        pdf_path = Path(source)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {source}")

        if marker_pdf is None:
            raise ImportError("marker_pdf is required for PDF extraction")

        try:
            if hasattr(marker_pdf, "to_text_with_layout"):
                text, layout = marker_pdf.to_text_with_layout(pdf_path)
            else:
                layout = None
                text = marker_pdf.to_text(pdf_path)
        except Exception as e:  # pragma: no cover - passthrough any extraction errors
            raise RuntimeError(f"Failed to extract PDF: {e}")

        metadata = {
            "source_type": "pdf",
            "file_name": pdf_path.name,
        }
        if layout is not None:
            metadata["layout"] = layout
        return {"text": text, "metadata": metadata}
