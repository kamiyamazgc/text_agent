import os
import sys
import importlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


def test_import_processors_without_optional_deps(monkeypatch):
    for pkg in [
        "openai",
        "language_tool_python",
        "sacrebleu",
        "langdetect",
        "fugashi",
    ]:
        monkeypatch.setitem(sys.modules, pkg, None)

    for mod in list(sys.modules):
        if mod.startswith("docpipe.processors"):
            monkeypatch.delitem(sys.modules, mod, raising=False)

    processors = importlib.import_module("docpipe.processors")

    assert processors.Preprocessor is not None
    assert processors.Fixer is not None
    assert processors.SpellChecker is not None
    assert len(processors.__all__) == len(set(processors.__all__))
