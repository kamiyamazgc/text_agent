import os
import sys
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docpipe.extractors.web import WebExtractor  # noqa: E402


def _dummy_trafilatura_module(

    fetch_returns: str = "DUMMY",
    extract_returns: str = "TEXT",
    meta_returns: dict | None = None,
):
    return types.SimpleNamespace(
        fetch_url=lambda url: fetch_returns,
        extract=lambda html, include_comments=False, include_tables=False: extract_returns,
        metadata=types.SimpleNamespace(extract_metadata=lambda html: meta_returns),
    )


def test_can_handle_web():
    extractor = WebExtractor()
    assert extractor.can_handle("https://example.com")
    assert not extractor.can_handle("file.pdf")


def test_extract_success(monkeypatch):
    dummy = _dummy_trafilatura_module()
    monkeypatch.setattr(
        "docpipe.extractors.web.trafilatura",
        dummy,
    )
    monkeypatch.setattr(
        "docpipe.extractors.web.extract_metadata",
        dummy.metadata.extract_metadata,
    )
    extractor = WebExtractor()
    result = extractor.extract("https://example.com")
    assert result["text"] == "TEXT"
    assert result["metadata"]["source_type"] == "web"


def test_extract_with_metadata(monkeypatch):
    dummy = _dummy_trafilatura_module(meta_returns={"title": "Example"})
    monkeypatch.setattr(
        "docpipe.extractors.web.trafilatura",
        dummy,
    )
    monkeypatch.setattr(
        "docpipe.extractors.web.extract_metadata",
        dummy.metadata.extract_metadata,
    )
    extractor = WebExtractor()
    result = extractor.extract("https://example.com")
    assert result["metadata"]["title"] == "Example"


def test_extract_missing_dependency(monkeypatch):
    monkeypatch.setattr("docpipe.extractors.web.trafilatura", None)
    extractor = WebExtractor()
    try:
        extractor.extract("https://example.com")
    except ImportError:
        assert True
    else:
        assert False, "ImportError not raised"


def test_extract_fetch_failure(monkeypatch):
    monkeypatch.setattr(
        "docpipe.extractors.web.trafilatura",
        _dummy_trafilatura_module(fetch_returns=None),
    )
    extractor = WebExtractor()
    try:
        extractor.extract("https://example.com")
    except RuntimeError:
        assert True
    else:
        assert False, "RuntimeError not raised"
