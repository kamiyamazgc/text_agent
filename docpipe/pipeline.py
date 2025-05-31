from __future__ import annotations

from typing import Any, Dict

from .config import Config
from .processors import Preprocessor, Translator, Proofreader, Evaluator, Fixer


def process_text(
    text: str,
    cfg: Config,
    preprocessor: Preprocessor | None = None,
    translator: Translator | None = None,
    proofreader: Proofreader | None = None,
    evaluator: Evaluator | None = None,
    fixer: Fixer | None = None,
) -> Dict[str, Any]:
    """Run the full processing pipeline with quality control."""

    pre = preprocessor or Preprocessor()
    tr = translator or Translator(cfg.llm.model, cfg.llm.temperature)
    pr = proofreader or Proofreader()
    ev = evaluator or Evaluator()
    fx = fixer or Fixer()

    # Preprocess and translate
    text = pre.process(text)
    trans_res = tr.process(text)
    text = trans_res["text"]
    metadata: Dict[str, Any] = dict(trans_res.get("metadata", {}))

    # Initial proofreading and evaluation
    pf_res = pr.process(text)
    text = pf_res["text"]
    quality = ev.evaluate(text)["quality_score"]
    retries = 0
    prev_quality = quality

    # Quality control loop
    while (
        quality < cfg.pipeline.quality_threshold
        and retries < cfg.pipeline.max_retries
    ):
        fix_res = fx.process(text)
        text = fix_res["text"]
        quality = ev.evaluate(text)["quality_score"]
        improvement = quality - prev_quality
        if improvement < cfg.pipeline.min_improvement:
            break
        prev_quality = quality
        retries += 1

    metadata["retries"] = retries
    metadata["quality_score"] = quality
    return {"text": text, "metadata": metadata, "quality_score": quality}
