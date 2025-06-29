import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docpipe.processors.preprocessor import Preprocessor  # noqa: E402


def test_restore_line_breaks_and_format():
    text = "This is a line\nbroken in the middle\nof a sentence.\n\nAnother line."
    pre = Preprocessor()
    processed = pre.process(text)
    assert (
        processed
        == "This is a line broken in the middle of a sentence.\n\nAnother line."
    )


def test_correct_ocr_errors():
    text = "ﬂ ﬁ “test” — example"
    pre = Preprocessor()
    processed = pre.process(text)
    assert "fl" in processed
    assert "fi" in processed
    assert '"test"' in processed
    assert "- example" in processed


def test_paragraph_break_inserts_blank_line():
    text = "First paragraph.\nSecond paragraph."
    pre = Preprocessor()
    processed = pre.process(text)
    assert processed == "First paragraph.\n\nSecond paragraph."


def test_multiple_blank_lines_collapse_to_one():
    text = "First.\n\n\nSecond."
    pre = Preprocessor()
    processed = pre.process(text)
    assert processed == "First.\n\nSecond."
