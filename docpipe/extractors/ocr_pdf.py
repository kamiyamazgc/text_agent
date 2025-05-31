from pathlib import Path
from typing import Any, Dict

try:
    import marker_ocr_pdf  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    marker_ocr_pdf = None  # type: ignore

from .base import BaseExtractor


class OCRPDFExtractor(BaseExtractor):
    """Extractor for scanned PDFs using marker-ocr-pdf"""

    def can_handle(self, source: str) -> bool:
        """Check if the source is a PDF file"""
        return source.lower().endswith(".pdf")

    def extract(self, source: str, **kwargs: Any) -> Dict[str, Any]:
        """Extract text from a scanned PDF via OCR, returning confidence."""
        pdf_path = Path(source)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {source}")

        if marker_ocr_pdf is None:
            raise ImportError("marker_ocr_pdf is required for OCR PDF extraction")

        try:
            if hasattr(marker_ocr_pdf, "to_text_with_confidence"):
                text, confidence = marker_ocr_pdf.to_text_with_confidence(pdf_path)
            else:
                confidence = None
                text = marker_ocr_pdf.to_text(pdf_path)
        except Exception as e:  # pragma: no cover - passthrough any extraction errors
            raise RuntimeError(f"Failed to OCR PDF: {e}")

        metadata = {
            "source_type": "ocr_pdf",
            "file_name": pdf_path.name,
        }
        if confidence is not None:
            metadata["confidence"] = confidence
        return {"text": text, "metadata": metadata}
