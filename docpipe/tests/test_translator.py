import os
import sys
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docpipe.processors.translator import Translator  # noqa: E402


def _dummy_openai_module(result: str = "翻訳済み"):
    class DummyChatCompletion:
        @staticmethod
        def create(model, messages, temperature=0.0):
            return {"choices": [{"message": {"content": result}}]}

    return types.SimpleNamespace(ChatCompletion=DummyChatCompletion)


def _capture_openai_module(store: dict):
    class DummyCompletions:
        @staticmethod
        def create(model, messages, temperature=0.0):
            store["prompt"] = messages[0]["content"]
            class DummyMessage:
                content = "翻訳済み"
            class DummyChoice:
                message = DummyMessage()
            class DummyResponse:
                choices = [DummyChoice()]
            return DummyResponse()
    class DummyChat:
        completions = DummyCompletions
    class DummyOpenAI:
        chat = DummyChat()
    return DummyOpenAI()


def test_translate(monkeypatch):
    monkeypatch.setattr(
        "docpipe.processors.translator.openai", _dummy_openai_module("こんにちは")
    )
    tr = Translator()
    out = tr.process("Hello")
    assert out["text"] == "こんにちは"
    assert out["metadata"]["source_language"] == "en"


def test_detect_language_japanese(monkeypatch):
    monkeypatch.setattr("docpipe.processors.translator.openai", _dummy_openai_module())
    tr = Translator()
    assert tr.detect_language("これは日本語です") == "ja"


def test_custom_prompt(monkeypatch):
    store = {}
    dummy_openai = _capture_openai_module(store)
    monkeypatch.setattr("docpipe.processors.translator.openai", dummy_openai)
    monkeypatch.setattr("docpipe.processors.translator.OpenAI", lambda: dummy_openai)
    tr = Translator(prompt="P: {text} -> {target_lang}")
    tr.translate("Hello", "fr")
    assert store["prompt"] == "P: Hello -> fr"
