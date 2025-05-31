from typing import Any, Dict, List

from .config import PipelineConfig
from .processors import Translator, Proofreader, Evaluator, Fixer
from .utils import split_into_chunks


def _process_chunk(
    text: str,
    cfg: PipelineConfig,
    translator: Translator,
    proofreader: Proofreader,
    evaluator: Evaluator,
    fixer: Fixer,
) -> Dict[str, Any]:
    """Process a single text chunk through the pipeline."""
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


def process_text(
    text: str,

    cfg: PipelineConfig,
    translator: Translator,
    proofreader: Proofreader,
    evaluator: Evaluator,
    fixer: Fixer,
    max_tokens: int = 2048,
) -> Dict[str, Any]:
    """Run text through translation, proofreading, evaluation and fixing.

    The text is split into chunks with :func:`split_into_chunks` and each chunk
    is processed sequentially. Metadata from all chunks is aggregated and
    returned alongside the concatenated text.
    """

    chunks = split_into_chunks(text, max_tokens)

    if len(chunks) == 1:
        return _process_chunk(
            chunks[0], cfg, translator, proofreader, evaluator, fixer
        )

    all_text: List[str] = []
    meta_list: List[Dict[str, Any]] = []
    quality_sum = 0.0
    retry_sum = 0

    for chunk in chunks:
        result = _process_chunk(chunk, cfg, translator, proofreader, evaluator, fixer)
        all_text.append(result["text"])
        m = result["metadata"]
        meta_list.append(m)
        quality_sum += m.get("quality_score", 0.0)
        retry_sum += m.get("retries", 0)

    aggregated: Dict[str, Any] = {
        "quality_score": quality_sum / len(meta_list) if meta_list else 0.0,
        "retries": retry_sum,
        "chunks": meta_list,
    }

    joined_text = " ".join(t.strip() for t in all_text if t)
    return {"text": joined_text, "metadata": aggregated}
