from pathlib import Path
from typing import Optional

try:  # optional dependency
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional
    yaml = None  # type: ignore
from pydantic import BaseModel

class PipelineConfig(BaseModel):
    quality_threshold: float = 0.75
    max_retries: int = 3
    min_improvement: float = 0.005
    language_tool_threshold: float = 0.02
    bleu_threshold: float = 35.0

class LLMConfig(BaseModel):
    profile: str = "default"  # "default" or "local"
    model: str = "gpt-4.1-mini"
    temperature: float = 0.7

class TranslatorConfig(BaseModel):
    model: str = "gpt-4.1-mini"
    temperature: float = 0.7
    prompt: str = "Translate the following text to {target_lang}:\n{text}"

class ProofreaderConfig(BaseModel):
    model: str = "gpt-4.1-mini"
    style: str = "general"
    temperature: float = 0.0
    prompt: str = (
        "Proofread the following text. Fix grammar, style, and readability "
        "issues in {style} style. Return only the corrected text."
    )

class WhisperConfig(BaseModel):
    model: str = "large"
    language: Optional[str] = None

class Config(BaseModel):
    pipeline: PipelineConfig = PipelineConfig()
    llm: LLMConfig = LLMConfig()
    translator: TranslatorConfig = TranslatorConfig()
    proofreader: ProofreaderConfig = ProofreaderConfig()
    whisper: WhisperConfig = WhisperConfig()
    output_dir: Path = Path("output")
    temp_dir: Path = Path("temp")
    log_dir: Path = Path("logs")

    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        if yaml is None:
            raise ImportError("PyYAML is required to load configuration files")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    @classmethod
    def load(cls, path: Optional[str] = None) -> "Config":
        """Load configuration from YAML file if available."""
        if path:
            return cls.from_yaml(path)

        default_path = Path("config.yaml")
        if default_path.exists():
            return cls.from_yaml(str(default_path))

        return cls()

    def to_yaml(self, path: str) -> None:
        if yaml is None:
            raise ImportError("PyYAML is required to write configuration files")
        with open(path, "w", encoding="utf-8") as f:
            try:
                data = self.model_dump()  # Pydantic v2
            except AttributeError:  # pragma: no cover - Pydantic v1 fallback
                data = self.dict()  # type: ignore[attr-defined]
            yaml.dump(data, f, allow_unicode=True)
