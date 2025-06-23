import csv
from pathlib import Path
from typing import Dict

try:  # optional dependency
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional
    yaml = None  # type: ignore

import re


class Glossary:
    """Load bilingual glossary from CSV or YAML and replace terms."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.mapping: Dict[str, str] = {}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            raise FileNotFoundError(self.path)
        if self.path.suffix.lower() in {".yaml", ".yml"}:
            self._load_yaml()
        elif self.path.suffix.lower() == ".csv":
            self._load_csv()
        else:
            raise ValueError("Unsupported glossary format: %s" % self.path)

    def _add_entry(self, ja: str, en: str) -> None:
        if ja:
            self.mapping[ja] = ja
        if en:
            self.mapping[en] = ja

    def _load_csv(self) -> None:
        with open(self.path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ja = row.get("ja") or row.get("jp") or row.get("term") or ""
                en = row.get("en") or ""
                if ja or en:
                    self._add_entry(ja.strip(), en.strip())

    def _load_yaml(self) -> None:
        if yaml is None:
            raise ImportError("PyYAML is required for YAML glossary")
        with open(self.path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or []
        for item in data:
            if not isinstance(item, dict):
                continue
            ja = str(item.get("ja", "")).strip()
            en = str(item.get("en", "")).strip()
            if ja or en:
                self._add_entry(ja, en)

    def replace(self, text: str) -> str:
        if not self.mapping:
            return text
        # replace longer terms first
        items = sorted(self.mapping.items(), key=lambda x: len(x[0]), reverse=True)
        for term, canonical in items:
            if not term:
                continue
            if re.fullmatch(r"[A-Za-z0-9_\-]+", term):
                pattern = r"(?<![A-Za-z0-9_])" + re.escape(term) + r"(?![A-Za-z0-9_])"
            else:
                pattern = re.escape(term)
            text = re.sub(pattern, canonical, text)
        return text
