from pathlib import Path
from typing import Any, Dict, Tuple

try:
    import whisper  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    whisper = None  # type: ignore

from .base import BaseExtractor


class AudioExtractor(BaseExtractor):
    """Extractor for audio files using OpenAI Whisper."""

    SUPPORTED_EXTENSIONS: Tuple[str, ...] = (".mp3", ".wav", ".m4a")

    def __init__(self, model: str = "large") -> None:
        if whisper is None:
            raise ImportError("openai-whisper is required for audio extraction")
        self.model_name = model
        self.whisper_model = whisper.load_model(model)

    def can_handle(self, source: str) -> bool:
        """Check if the source is an audio file"""
        return source.lower().endswith(self.SUPPORTED_EXTENSIONS)

    def extract(self, source: str, **kwargs: Any) -> Dict[str, Any]:
        """Transcribe the audio file"""
        audio_path = Path(source)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio not found: {source}")

        result = self.whisper_model.transcribe(
            str(audio_path),
            language=kwargs.get("language"),
            verbose=False,
        )

        segments = result.get("segments", [])
        transcript_lines = []
        for idx, seg in enumerate(segments, 1):
            start = seg.get("start", 0.0)
            end = seg.get("end", 0.0)
            text = seg.get("text", "").strip()
            speaker = f"speaker_{(idx % 2) + 1}"  # TODO: real diarization
            transcript_lines.append(f"[{start:.2f}-{end:.2f}] {speaker}: {text}")

        text = "\n".join(transcript_lines) if transcript_lines else result.get("text", "")

        metadata = {
            "source_type": "audio",
            "file_name": audio_path.name,
            "model": self.model_name,
        }
        return {"text": text, "metadata": metadata}
