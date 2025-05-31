from .base import BaseExtractor

try:  # Optional dependency
    from .youtube import YouTubeExtractor
except Exception:  # pragma: no cover - optional
    YouTubeExtractor = None  # type: ignore

from .pdf import PDFExtractor
from .ocr_pdf import OCRPDFExtractor

try:  # Optional dependency
    from .web import WebExtractor
except Exception:  # pragma: no cover - optional
    WebExtractor = None  # type: ignore

try:  # Optional dependency
    from .audio import AudioExtractor
except Exception:  # pragma: no cover - optional
    AudioExtractor = None  # type: ignore

__all__ = ["BaseExtractor", "PDFExtractor", "OCRPDFExtractor"]

if AudioExtractor is not None:
    __all__.insert(1, "AudioExtractor")

if YouTubeExtractor is not None:
    __all__.insert(1, "YouTubeExtractor")

if WebExtractor is not None:
    __all__.insert(1, "WebExtractor")

