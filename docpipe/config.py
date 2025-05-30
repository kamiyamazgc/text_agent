from pathlib import Path
from typing import Dict, Any
import yaml
from pydantic import BaseModel

class PipelineConfig(BaseModel):
    quality_threshold: float = 0.85
    max_retries: int = 3
    min_improvement: float = 0.01
    language_tool_threshold: float = 0.02
    bleu_threshold: float = 35.0

class LLMConfig(BaseModel):
    profile: str = "default"  # "default" or "local"
    model: str = "gpt-4"
    temperature: float = 0.7

class Config(BaseModel):
    pipeline: PipelineConfig = PipelineConfig()
    llm: LLMConfig = LLMConfig()
    output_dir: Path = Path("output")
    temp_dir: Path = Path("temp")
    log_dir: Path = Path("logs")

    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def to_yaml(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(self.model_dump(), f, allow_unicode=True) 