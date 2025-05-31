import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docpipe.extractors.plain import PlainTextExtractor  # noqa: E402


def test_can_handle_plain():
    extractor = PlainTextExtractor()
    assert extractor.can_handle("sample.txt")
    assert extractor.can_handle("sample.MD")
    assert not extractor.can_handle("sample.pdf")


def test_extract_success(tmp_path):
    file = tmp_path / "sample.txt"
    file.write_text("hello", encoding="utf-8")
    extractor = PlainTextExtractor()
    result = extractor.extract(str(file))
    assert result["text"] == "hello"
    assert result["metadata"]["source_type"] == "plain"
    assert result["metadata"]["file_name"] == "sample.txt"


def test_extract_file_not_found():
    extractor = PlainTextExtractor()
    with pytest.raises(FileNotFoundError):
        extractor.extract("missing.txt")
