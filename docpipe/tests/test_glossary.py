import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import yaml

from docpipe.glossary import Glossary


def test_load_csv(tmp_path):
    gfile = tmp_path / "gl.csv"
    gfile.write_text("ja,en\n人工知能,AI\n", encoding="utf-8")
    gl = Glossary(str(gfile))
    assert gl.replace("AIを研究する") == "人工知能を研究する"


def test_load_yaml(tmp_path):
    gfile = tmp_path / "gl.yaml"
    yaml.dump([{"ja": "パソコン", "en": "computer"}], gfile.open("w", encoding="utf-8"), allow_unicode=True)
    gl = Glossary(str(gfile))
    assert gl.replace("computerを使う") == "パソコンを使う"

