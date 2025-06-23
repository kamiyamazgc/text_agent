from typing import Any, Dict, List

from .config import Config
from .processors import Translator, Proofreader, Evaluator, Fixer, SpellChecker
from .processors.evaluator import EvaluationResult
from .utils import split_into_chunks


def _process_chunk(
    text: str,
    cfg: Config,
    translator: Translator,
    proofreader: Proofreader,
    evaluator: Evaluator,
    fixer: Fixer,
    spellchecker: SpellChecker,
) -> Dict[str, Any]:
    """Process a single text chunk through the pipeline."""
    prev_quality = 0.0
    metadata: Dict[str, Any] = {}

    for retries in range(cfg.pipeline.max_retries + 1):
        trans = translator.process(text)
        text = trans["text"]
        metadata.update(trans.get("metadata", {}))

        if cfg.proofreader.enabled:
            pf = proofreader.process(text)
            text = pf["text"]
            metadata["proofread_quality"] = pf.get("quality_score")

        eval_result: EvaluationResult = evaluator.evaluate(text)
        quality: float = eval_result["quality_score"]

        err_rate = eval_result.get("grammar_error_rate")
        if err_rate is not None and err_rate > cfg.pipeline.language_tool_threshold:
            quality = 0.0

        bleu_score = eval_result.get("bleu_score")
        if bleu_score is not None and bleu_score < cfg.pipeline.bleu_threshold:
            quality = 0.0

        eval_result["quality_score"] = quality
        metadata.update(eval_result)

        # 品質が閾値を上回った場合は成功
        if quality >= cfg.pipeline.quality_threshold:
            break

        # 最大リトライ回数に達した場合は停止
        if retries >= cfg.pipeline.max_retries:
            break

        # リトライ時の改善幅が設定値以下なら停止
        if retries > 0:
            improvement = quality - prev_quality
            if improvement <= cfg.pipeline.min_improvement:
                break

        fix_result = fixer.process(text)
        text = fix_result["text"]

        prev_quality = quality

    # 品質が閾値未満の場合のみSpellCheckerを実行
    if quality < spellchecker.quality_threshold:
        spell_result = spellchecker.process(text, quality)
        text = spell_result["text"]
        metadata.update(spell_result.get("metadata", {}))

    metadata["retries"] = retries

    return {"text": text, "metadata": metadata}


def process_text(
    text: str,

    cfg: Config,
    translator: Translator,
    proofreader: Proofreader,
    evaluator: Evaluator,
    fixer: Fixer,
    spellchecker: SpellChecker,
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
            chunks[0], cfg, translator, proofreader, evaluator, fixer, spellchecker
        )

    all_text: List[str] = []
    meta_list: List[Dict[str, Any]] = []
    quality_sum = 0.0
    retry_sum = 0

    for chunk in chunks:
        result = _process_chunk(chunk, cfg, translator, proofreader, evaluator, fixer, spellchecker)
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
