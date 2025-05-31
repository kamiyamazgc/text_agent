import os
import sys
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docpipe.extractors.pdf import PDFExtractor  # noqa: E402


def test_extract_with_layout(tmp_path, monkeypatch):
    fake_pdf = tmp_path / "sample.pdf"
    fake_pdf.write_text("dummy")

    dummy_module = types.SimpleNamespace(
        to_text_with_layout=lambda p: ("PDF TEXT", ["page1", "page2"])
    )
    monkeypatch.setattr("docpipe.extractors.pdf.marker_pdf", dummy_module)

    extractor = PDFExtractor()
    result = extractor.extract(str(fake_pdf))
    assert result["text"] == "PDF TEXT"
    assert result["metadata"]["layout"] == ["page1", "page2"]
