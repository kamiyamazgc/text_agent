from .base import BaseExtractor

try:  # Optional dependency
    from .youtube import YouTubeExtractor
except Exception:  # pragma: no cover - optional
    YouTubeExtractor = None  # type: ignore

from .pdf import PDFExtractor
from .ocr_pdf import OCRPDFExtractor

__all__ = ["BaseExtractor", "PDFExtractor", "OCRPDFExtractor"]

if YouTubeExtractor is not None:
    __all__.insert(1, "YouTubeExtractor")

