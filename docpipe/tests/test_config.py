import os
import pytest
from pathlib import Path

from docpipe.config import Config


def test_load_default_file(tmp_path, monkeypatch):
    pytest.importorskip("yaml")
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text("llm:\n  model: gpt-3\n")

    # change working directory to tmp_path
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        cfg = Config.load()
    finally:
        os.chdir(cwd)
    assert cfg.llm.model == "gpt-3"


def test_load_no_file(tmp_path, monkeypatch):
    pytest.importorskip("yaml")
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        cfg = Config.load()
    finally:
        os.chdir(cwd)
    assert cfg.pipeline.quality_threshold == 0.85


