import os
import sys
import types
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docpipe.extractors.ocr_pdf import OCRPDFExtractor  # noqa: E402


def test_can_handle_pdf():
    extractor = OCRPDFExtractor()
    assert extractor.can_handle("sample.pdf")


def test_extract_success(tmp_path, monkeypatch):
    fake_pdf = tmp_path / "sample.pdf"
    fake_pdf.write_text("dummy")

    dummy_module = types.SimpleNamespace(to_text=lambda p: "OCR TEXT")
    monkeypatch.setattr("docpipe.extractors.ocr_pdf.marker_ocr_pdf", dummy_module)

    extractor = OCRPDFExtractor()
    result = extractor.extract(str(fake_pdf))
    assert result["text"] == "OCR TEXT"
    assert result["metadata"]["source_type"] == "ocr_pdf"


def test_extract_missing_dependency(tmp_path, monkeypatch):
    fake_pdf = tmp_path / "sample.pdf"
    fake_pdf.write_text("dummy")

    monkeypatch.setattr("docpipe.extractors.ocr_pdf.marker_ocr_pdf", None)

    extractor = OCRPDFExtractor()
    with pytest.raises(ImportError):
        extractor.extract(str(fake_pdf))
