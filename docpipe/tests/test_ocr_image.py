import os
import sys
import types
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docpipe.extractors.ocr_image import OCRImageExtractor  # noqa: E402


def test_can_handle_image():
    extractor = OCRImageExtractor()
    assert extractor.can_handle("photo.png")
    assert extractor.can_handle("photo.JPG")
    assert not extractor.can_handle("document.pdf")


def test_extract_success(tmp_path, monkeypatch):
    img = tmp_path / "img.png"
    img.write_bytes(b"dummy")

    dummy_pytesseract = types.SimpleNamespace(image_to_string=lambda img, lang=None: "TEXT")
    dummy_image = types.SimpleNamespace(open=lambda p: "IMG")
    monkeypatch.setattr("docpipe.extractors.ocr_image.pytesseract", dummy_pytesseract)
    monkeypatch.setattr("docpipe.extractors.ocr_image.Image", dummy_image)

    extractor = OCRImageExtractor()
    result = extractor.extract(str(img))
    assert result["text"] == "TEXT"
    assert result["metadata"]["source_type"] == "ocr_image"
    assert result["metadata"]["file_name"] == "img.png"


def test_extract_file_not_found(monkeypatch):
    dummy_pytesseract = types.SimpleNamespace(image_to_string=lambda img, lang=None: "TEXT")
    dummy_image = types.SimpleNamespace(open=lambda p: "IMG")
    monkeypatch.setattr("docpipe.extractors.ocr_image.pytesseract", dummy_pytesseract)
    monkeypatch.setattr("docpipe.extractors.ocr_image.Image", dummy_image)

    extractor = OCRImageExtractor()
    with pytest.raises(FileNotFoundError):
        extractor.extract("missing.png")


def test_extract_missing_dependency(tmp_path, monkeypatch):
    img = tmp_path / "img.png"
    img.write_bytes(b"dummy")

    monkeypatch.setattr("docpipe.extractors.ocr_image.pytesseract", None)
    monkeypatch.setattr("docpipe.extractors.ocr_image.Image", None)
    extractor = OCRImageExtractor()
    with pytest.raises(ImportError):
        extractor.extract(str(img))
