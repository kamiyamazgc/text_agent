from pathlib import Path
from typing import Any, Dict

try:
    import pypdfium2  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pypdfium2 = None  # type: ignore

from . import marker_pdf

from .base import BaseExtractor


class PDFExtractor(BaseExtractor):
    """Extractor for digital PDFs using marker-pdf with pypdfium2 fallback."""

    def can_handle(self, source: str) -> bool:
        """Check if the source is a PDF file"""
        return source.lower().endswith(".pdf")

    def extract(self, source: str, **kwargs: Any) -> Dict[str, Any]:
        """Extract text from a digital PDF with optional layout information."""
        pdf_path = Path(source)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {source}")

        # Prefer marker-pdf backend if available
        try:
            text, layout = marker_pdf.to_text_with_layout(str(pdf_path))
            metadata = {
                "source_type": "pdf",
                "file_name": pdf_path.name,
                "layout": layout,
            }
            return {"text": text, "metadata": metadata}
        except ImportError:
            pass

        if pypdfium2 is None:
            raise ImportError(
                "marker-pdf or pypdfium2 is required for PDF extraction"
            )

        try:
            # Open PDF and extract text
            pdf = pypdfium2.PdfDocument(pdf_path)
            text_parts = []
            
            # Extract text from each page
            for page_index in range(len(pdf)):
                page = pdf[page_index]
                text_page = page.get_textpage()
                text_parts.append(text_page.get_text_range())
                text_page.close()
            
            text = "\n".join(text_parts)
            pdf.close()
            
        except Exception as e:  # pragma: no cover - passthrough any extraction errors
            raise RuntimeError(f"Failed to extract PDF: {e}")

        metadata = {
            "source_type": "pdf",
            "file_name": pdf_path.name,
        }
        return {"text": text, "metadata": metadata}
