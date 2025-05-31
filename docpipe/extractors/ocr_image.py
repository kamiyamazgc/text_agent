from pathlib import Path
from typing import Any, Dict, Tuple

try:
    import pytesseract  # type: ignore
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pytesseract = None  # type: ignore
    Image = None  # type: ignore

from .base import BaseExtractor


class OCRImageExtractor(BaseExtractor):
    """Extractor for images using Tesseract OCR."""

    SUPPORTED_EXTENSIONS: Tuple[str, ...] = (".png", ".jpg", ".jpeg")

    def can_handle(self, source: str) -> bool:
        """Check if the source is a supported image file."""
        return source.lower().endswith(self.SUPPORTED_EXTENSIONS)

    def extract(self, source: str, **kwargs: Any) -> Dict[str, Any]:
        """Perform OCR on the image and return extracted text."""
        if pytesseract is None or Image is None:
            raise ImportError("pytesseract and Pillow are required for image OCR")

        img_path = Path(source)
        if not img_path.exists():
            raise FileNotFoundError(f"Image not found: {source}")

        try:
            image = Image.open(img_path)
            text = pytesseract.image_to_string(image, lang=kwargs.get("lang"))
        except Exception as e:  # pragma: no cover - passthrough OCR errors
            raise RuntimeError(f"Failed to OCR image: {e}") from e

        metadata = {
            "source_type": "ocr_image",
            "file_name": img_path.name,
        }
        return {"text": text, "metadata": metadata}
