from typing import Dict, Any

try:
    import trafilatura  # type: ignore
    from trafilatura.metadata import extract_metadata  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    trafilatura = None  # type: ignore
    extract_metadata = None  # type: ignore

from .base import BaseExtractor


class WebExtractor(BaseExtractor):
    """Extractor for web pages using trafilatura."""

    def can_handle(self, source: str) -> bool:
        """Check if the source is a URL."""
        return source.lower().startswith("http://") or source.lower().startswith("https://")

    def extract(self, source: str, **kwargs: Any) -> Dict[str, Any]:
        """Extract main content from a web page."""
        if trafilatura is None:
            raise ImportError("trafilatura is required for web extraction")

        downloaded = trafilatura.fetch_url(source)
        if not downloaded:
            raise RuntimeError(f"Failed to fetch URL: {source}")

        text = trafilatura.extract(
            downloaded, include_comments=False, include_tables=False
        )
        if text is None:
            raise RuntimeError(f"Failed to extract content from {source}")

        metadata = {
            "source_type": "web",
            "url": source,
        }

        if extract_metadata is not None:
            meta = extract_metadata(downloaded)
            if meta:
                for key, value in meta.items():
                    if value:
                        metadata[key] = value

        return {"text": text, "metadata": metadata}
