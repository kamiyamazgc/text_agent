import os
import pytest

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


def test_translator_config_loaded(tmp_path):
    pytest.importorskip("yaml")
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(
        "translator:\n  model: gpt-3\n  temperature: 0.5\n  prompt: t:{text}\n",
        encoding="utf-8",
    )

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        cfg = Config.load()
    finally:
        os.chdir(cwd)

    assert cfg.translator.model == "gpt-4.1-mini"
    assert cfg.translator.temperature == 0.5
    assert cfg.translator.prompt == "t:{text}"


def test_load_no_file(tmp_path, monkeypatch):
    pytest.importorskip("yaml")
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        cfg = Config.load()
    finally:
        os.chdir(cwd)
    assert cfg.pipeline.quality_threshold == 0.85


def test_translator_default_values():
    cfg = Config()
    assert cfg.translator.model == "gpt-4"
    assert cfg.translator.temperature == 0.7
    assert cfg.translator.prompt.startswith("Translate the following text")


def test_proofreader_config_loaded(tmp_path):
    pytest.importorskip("yaml")
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(
        "proofreader:\n  model: p1\n  style: fancy\n  temperature: 0.2\n  prompt: P {style}\n",
        encoding="utf-8",
    )

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        cfg = Config.load()
    finally:
        os.chdir(cwd)

    assert cfg.proofreader.model == "gpt-4.1-mini"
    assert cfg.proofreader.style == "fancy"
    assert cfg.proofreader.temperature == 0.2
    assert cfg.proofreader.prompt == "P {style}"


def test_proofreader_default_values():
    cfg = Config()
    assert cfg.proofreader.model == "gpt-4o"
    assert cfg.proofreader.style == "general"
    assert cfg.proofreader.temperature == 0.0
    assert "{style}" in cfg.proofreader.prompt


def test_whisper_config_loaded(tmp_path):
    pytest.importorskip("yaml")
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(
        "whisper:\n  model: tiny\n  language: en\n",
        encoding="utf-8",
    )

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        cfg = Config.load()
    finally:
        os.chdir(cwd)

    assert cfg.whisper.model == "tiny"
    assert cfg.whisper.language == "en"


def test_whisper_default_values():
    cfg = Config()
    assert cfg.whisper.model == "large"
    assert cfg.whisper.language is None


