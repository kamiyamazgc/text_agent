import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docpipe.processors.fixer import Fixer  # noqa: E402


def test_remove_duplicate_lines():
    fixer = Fixer()
    text = "Line1\nLine1\nLine2"
    result = fixer.process(text)
    assert result["text"] == "Line1\nLine2"
    assert result["changed"]


def test_balance_parentheses():
    fixer = Fixer()
    text = "Example (text"
    result = fixer.process(text)
    assert result["text"].endswith(")")


def test_fix_common_typos():
    fixer = Fixer()
    text = "teh quick brown fox"
    result = fixer.process(text)
    assert "the quick brown fox" == result["text"]


def test_remove_llm_disclaimer_fix_note():
    fixer = Fixer()
    text = "ここでは文章を修正しました。\n実際の内容です。"
    result = fixer.process(text)
    assert "ここでは" not in result["text"]
    assert result["text"].startswith("実際の内容です")


def test_remove_llm_disclaimer_translation_note():
    fixer = Fixer()
    text = "こちらが翻訳です:\nHello"
    result = fixer.process(text)
    assert result["text"] == "Hello"
