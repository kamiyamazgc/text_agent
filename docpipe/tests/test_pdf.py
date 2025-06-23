import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docpipe.extractors.pdf import PDFExtractor  # noqa: E402
import pytest


def test_extract_with_layout(tmp_path, monkeypatch):
    fake_pdf = tmp_path / "sample.pdf"
    fake_pdf.write_text("dummy")

    monkeypatch.setattr(
        "docpipe.extractors.pdf.marker_pdf.to_text_with_layout",
        lambda p: ("PDF TEXT", ["page1", "page2"]),
    )

    extractor = PDFExtractor()
    result = extractor.extract(str(fake_pdf))
    assert result["text"] == "PDF TEXT"
    assert result["metadata"]["layout"] == ["page1", "page2"]


def test_extract_missing_dependency(tmp_path, monkeypatch):
    fake_pdf = tmp_path / "sample.pdf"
    fake_pdf.write_text("dummy")

    def raise_import(_):
        raise ImportError("missing")

    monkeypatch.setattr(
        "docpipe.extractors.pdf.marker_pdf.to_text_with_layout",
        raise_import,
    )
    monkeypatch.setattr("docpipe.extractors.pdf.pypdfium2", None)

    extractor = PDFExtractor()
    with pytest.raises(ImportError):
        extractor.extract(str(fake_pdf))
