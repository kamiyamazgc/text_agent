from typing import Any, Dict

from .config import PipelineConfig
from .processors import Translator, Proofreader, Evaluator, Fixer


def process_text(
    text: str,
    cfg: PipelineConfig,
    translator: Translator,
    proofreader: Proofreader,
    evaluator: Evaluator,
    fixer: Fixer,
) -> Dict[str, Any]:
    """Run text through translation, proofreading, evaluation and fixing."""
    retries = 0
    prev_quality = 0.0
    metadata: Dict[str, Any] = {}
    while True:
        trans = translator.process(text)
        text = trans["text"]
        metadata.update(trans.get("metadata", {}))

        pf = proofreader.process(text)
        text = pf["text"]
        metadata["proofread_quality"] = pf.get("quality_score")

        eval_result = evaluator.evaluate(text)
        quality = eval_result["quality_score"]
        metadata.update(eval_result)

        if quality >= cfg.quality_threshold:
            break

        if retries >= cfg.max_retries:
            break

        improvement = quality - prev_quality
        if improvement < cfg.min_improvement:
            break

        fix_result = fixer.process(text)
        text = fix_result["text"]
        prev_quality = quality
        retries += 1

    metadata["retries"] = retries
    return {"text": text, "metadata": metadata}
