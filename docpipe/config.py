from pathlib import Path
from typing import Optional

try:  # optional dependency
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional
    yaml = None  # type: ignore
from pydantic import BaseModel

class PipelineConfig(BaseModel):
    quality_threshold: float = 0.85
    max_retries: int = 3
    min_improvement: float = 0.005
    language_tool_threshold: float = 0.02
    bleu_threshold: float = 35.0

class LLMConfig(BaseModel):
    profile: str = "default"  # "default" or "local"
    model: str = "gpt-4.1-mini"
    temperature: float = 0.7

class TranslatorConfig(BaseModel):
    model: str = "gpt-4"
    temperature: float = 0.7
    prompt: str = (
        "Translate the following text to {target_lang}:\n{text}\n"
        "翻訳結果のみを返してください。"
    )

class ProofreaderConfig(BaseModel):
    model: str = "gpt-4o"
    style: str = "general"
    temperature: float = 0.0
    enabled: bool = True
    prompt: str = (
        "Proofread the following text. Fix grammar, style, and readability "
        "issues in {style} style. 文の意味を変えないこと。未知の用語はそのまま残すこと。"
        "結果だけを出力してください。"
    )

class WhisperConfig(BaseModel):
    model: str = "large"
    language: Optional[str] = None
class GlossaryConfig(BaseModel):
    path: Optional[Path] = None
    enabled: bool = False


class Config(BaseModel):
    pipeline: PipelineConfig = PipelineConfig()
    llm: LLMConfig = LLMConfig()
    translator: TranslatorConfig = TranslatorConfig()
    proofreader: ProofreaderConfig = ProofreaderConfig()
    whisper: WhisperConfig = WhisperConfig()
    glossary: GlossaryConfig = GlossaryConfig()
    output_dir: Path = Path("output")
    temp_dir: Path = Path("temp")
    log_dir: Path = Path("logs")
    output_extension: str = ".md"
    enable_markdown_headings: bool = True

    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        if yaml is None:
            raise ImportError("PyYAML is required to load configuration files")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        cfg = cls(**data)
        # ensure new option has default when missing
        cfg.output_extension = data.get("output_extension", ".md")
        cfg.enable_markdown_headings = data.get("enable_markdown_headings", True)
        # force default models regardless of file values for consistency
        cfg.translator.model = "gpt-4.1-mini"
        cfg.proofreader.model = "gpt-4.1-mini"
        return cfg

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
            data["output_extension"] = self.output_extension
            yaml.dump(data, f, allow_unicode=True)
