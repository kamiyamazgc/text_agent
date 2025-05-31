import re
from typing import Any, Dict

class Fixer:
    """Simple error correction agent."""

    def remove_duplicate_lines(self, text: str) -> str:
        lines = text.splitlines()
        cleaned: list[str] = []
        for line in lines:
            if not cleaned or line != cleaned[-1]:
                cleaned.append(line)
        return "\n".join(cleaned)

    def balance_parentheses(self, text: str) -> str:
        diff = text.count("(") - text.count(")")
        if diff > 0:
            text += ")" * diff
        elif diff < 0:
            text = "(" * (-diff) + text
        return text

    def fix_common_typos(self, text: str) -> str:
        corrections = {
            r"\bteh\b": "the",
            r"\brecieve\b": "receive",
        }
        for pattern, repl in corrections.items():
            text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
        text = re.sub(r" {2,}", " ", text)
        return text

    def process(self, text: str) -> Dict[str, Any]:
        original = text
        text = self.remove_duplicate_lines(text)
        text = self.balance_parentheses(text)
        text = self.fix_common_typos(text)
        changed = text != original
        return {"text": text, "changed": changed}
