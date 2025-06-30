import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docpipe.cli import _expand_sources  # noqa: E402
from docpipe import cli as cli_module  # noqa: E402


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


def test_cli_uses_whisper_model(monkeypatch):
    called = {}

    class DummyAE:
        def __init__(self, model: str = "large", language=None):
            called["model"] = model

        def can_handle(self, source):
            return False

        def extract(self, source):
            return {}

    monkeypatch.setattr(cli_module, "AudioExtractor", DummyAE)
    monkeypatch.setattr(cli_module, "_expand_sources", lambda s: [])

    class Dummy:
        def __init__(self, *a, **k):
            pass

        def process(self, text):
            return {"text": text, "metadata": {}}

    class DummyEval:
        def __init__(self, *a, **k):
            pass

        def evaluate(self, text, reference=None):
            return {"quality_score": 1.0}

    monkeypatch.setattr(cli_module, "Preprocessor", Dummy)
    monkeypatch.setattr(cli_module, "Translator", Dummy)
    monkeypatch.setattr(cli_module, "Proofreader", Dummy)
    monkeypatch.setattr(cli_module, "Fixer", Dummy)
    monkeypatch.setattr(cli_module, "Evaluator", DummyEval)

    cfg = cli_module.Config()
    cfg.whisper.model = "custom"
    monkeypatch.setattr(cli_module.Config, "load", classmethod(lambda cls, path=None: cfg))

    cli_module.process.callback(["dummy"], None, None, None)

    assert called["model"] == "custom"


def test_cli_uses_progressbar(monkeypatch, tmp_path):
    called = {}

    class DummyProgress:
        def __init__(self, iterable, label=None):
            called["called"] = True
            called["length"] = len(iterable)
            called["label"] = label
            self.iterable = iterable

        def __enter__(self):
            return self.iterable

        def __exit__(self, exc_type, exc, tb):
            pass

    monkeypatch.setattr(cli_module.click, "progressbar", DummyProgress)
    monkeypatch.setattr(cli_module, "_expand_sources", lambda s: ["a", "b"])

    class DummyExtractor:
        def __init__(self, *a, **k):
            pass

        def can_handle(self, source):
            return False

        def extract(self, source):
            return {}

    for name in [
        "YouTubeExtractor",
        "WebExtractor",
        "PDFExtractor",
        "OCRImageExtractor",
        "AudioExtractor",
        "PlainTextExtractor",
    ]:
        monkeypatch.setattr(cli_module, name, DummyExtractor)

    class Dummy:
        def __init__(self, *a, **k):
            pass

        def process(self, text):
            return {"text": text, "metadata": {}}

    class DummyEval(Dummy):
        def evaluate(self, text, reference=None):
            return {"quality_score": 1.0}

    monkeypatch.setattr(cli_module, "Preprocessor", Dummy)
    monkeypatch.setattr(cli_module, "Translator", Dummy)
    monkeypatch.setattr(cli_module, "Proofreader", Dummy)
    monkeypatch.setattr(cli_module, "Fixer", Dummy)
    monkeypatch.setattr(cli_module, "Evaluator", DummyEval)
    monkeypatch.setattr(cli_module, "SpellChecker", Dummy)
    monkeypatch.setattr(cli_module, "process_text", lambda *a, **k: {"text": "", "metadata": {}})

    cfg = cli_module.Config()
    cfg.output_dir = tmp_path
    monkeypatch.setattr(cli_module.Config, "load", classmethod(lambda cls, path=None: cfg))

    cli_module.process.callback(["dummy1", "dummy2"], None, None, None)

    assert called["called"]
    assert called["length"] == 2
    assert called["label"] == "Processing sources"
