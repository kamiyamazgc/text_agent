import os
import sys
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docpipe.utils import split_into_chunks  # noqa: E402


def test_split_into_chunks_word_fallback(monkeypatch):
    monkeypatch.setattr("docpipe.utils.text_utils.tiktoken", None)
    text = "one two three four five six seven eight nine"
    chunks = split_into_chunks(text, max_tokens=3)
    assert chunks == [
        "one two three",
        "four five six",
        "seven eight nine",
    ]


def test_split_into_chunks_with_dummy_tokenizer(monkeypatch):
    class DummyTokenizer:
        def encode(self, text: str):
            return text.split()

        def decode(self, tokens):
            return " ".join(tokens)

    dummy_module = types.SimpleNamespace(get_encoding=lambda name: DummyTokenizer())
    monkeypatch.setattr("docpipe.utils.text_utils.tiktoken", dummy_module)

    text = "one two three four five six seven eight nine"
    chunks = split_into_chunks(text, max_tokens=4)
    assert chunks == [
        "one two three four",
        "five six seven eight",
        "nine",
    ]


def test_split_into_chunks_handles_tiktoken_failure(monkeypatch):
    class FailingModule:
        def get_encoding(self, name):
            raise RuntimeError("download failed")

    monkeypatch.setattr("docpipe.utils.text_utils.tiktoken", FailingModule())

    text = "one two three four five six seven eight nine"
    chunks = split_into_chunks(text, max_tokens=3)
    assert chunks == [
        "one two three",
        "four five six",
        "seven eight nine",
    ]
