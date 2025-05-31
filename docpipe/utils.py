try:
    import tiktoken
except Exception:  # pragma: no cover - optional dependency
    tiktoken = None  # type: ignore

from typing import List


def split_into_chunks(text: str, max_tokens: int = 2048) -> List[str]:
    """Split text into chunks of roughly ``max_tokens`` tokens.

    Uses ``tiktoken`` when available. Otherwise falls back to a simple word
    based heuristic assuming roughly one token per word.
    """
    if max_tokens <= 0:
        return [text]

    if tiktoken is None:
        words = text.split()
        chunks = [" ".join(words[i : i + max_tokens]) for i in range(0, len(words), max_tokens)]
        return chunks or [""]

    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    pieces = [tokens[i : i + max_tokens] for i in range(0, len(tokens), max_tokens)]
    return [enc.decode(chunk) for chunk in pieces] or [""]
