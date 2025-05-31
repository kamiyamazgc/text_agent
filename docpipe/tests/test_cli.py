import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docpipe.cli import _expand_sources  # noqa: E402


def test_expand_sources(tmp_path):
    # Create files and a subdirectory
    file1 = tmp_path / "a.txt"
    file1.write_text("a")
    file2 = tmp_path / "b.txt"
    file2.write_text("b")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "c.txt").write_text("c")

    sources = [str(file1), str(tmp_path)]
    expanded = _expand_sources(sources)

    assert str(file1) in expanded
    assert str(file2) in expanded
    # subdirectory files should not be included
    assert str(sub / "c.txt") not in expanded


def test_expand_sources_urls_file(tmp_path):
    urls_file = tmp_path / "urls.txt"
    urls_file.write_text(
        "https://example.com\nnot-a-url\nhttp://example.org/page\n",
        encoding="utf-8",
    )

    sources = [str(urls_file)]
    expanded = _expand_sources(sources)

    assert expanded == [
        "https://example.com",
        "http://example.org/page",
    ]
