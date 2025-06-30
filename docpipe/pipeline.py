from typing import Any, Dict, List
import logging

from .config import Config
from .processors import Translator, Proofreader, Evaluator, Fixer, SpellChecker, DiffProcessor
from .processors.evaluator import EvaluationResult
from .utils import split_into_chunks

logger = logging.getLogger(__name__)


def _process_chunk(
    text: str,
    cfg: Config,
    translator: Translator,
    proofreader: Proofreader,
    evaluator: Evaluator,
    fixer: Fixer,
    spellchecker: SpellChecker,
    diff_processor: DiffProcessor = None,
) -> Dict[str, Any]:
    """Process a single text chunk through the pipeline."""
    prev_quality = 0.0
    prev_err_rate = None
    prev_readability = None
    metadata: Dict[str, Any] = {}

    for retries in range(cfg.pipeline.max_retries + 1):
        # 翻訳が有効な場合のみ実行
        if hasattr(cfg.translator, 'enabled') and cfg.translator.enabled:
            trans = translator.process(text)
            text = trans["text"]
            metadata.update(trans.get("metadata", {}))

        if cfg.proofreader.enabled:
            pf = proofreader.process(
                text, error_rate=prev_err_rate, readability=prev_readability
            )
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

        prev_err_rate = eval_result.get("grammar_error_rate")
        prev_readability = eval_result.get("readability_score")

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

    # DiffProcessorを実行（Proofreaderの後、品質が低い場合）
    logger.debug(
        "quality=%s, threshold=%s",
        quality,
        cfg.pipeline.diff_improvement_threshold,
    )
    logger.debug(
        "diff_processor=%s, enabled=%s",
        diff_processor is not None,
        cfg.diff_processor.enabled,
    )
    
    if (diff_processor and 
        cfg.diff_processor.enabled and 
        quality < cfg.pipeline.diff_improvement_threshold):
        
        logger.debug("DiffProcessor conditions met, executing...")
        diff_result = diff_processor.process(text)
        logger.debug("diff_result changed=%s", diff_result['metadata']['changed'])
        
        if diff_result["metadata"]["changed"]:
            text = diff_result["text"]
            metadata["diff_processor_applied"] = True
            metadata["diff_iterations"] = diff_result["metadata"]["iterations"]
            
            # DiffProcessor適用後の品質を再評価
            final_eval = evaluator.evaluate(text)
            metadata["final_quality_after_diff"] = final_eval["quality_score"]
            logger.debug("DiffProcessor applied successfully")
        else:
            logger.debug("DiffProcessor executed but no changes made")
    else:
        logger.debug("DiffProcessor conditions not met")

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
    diff_processor: DiffProcessor = None,
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
            chunks[0], cfg, translator, proofreader, evaluator, fixer, spellchecker, diff_processor
        )

    all_text: List[str] = []
    meta_list: List[Dict[str, Any]] = []
    quality_sum = 0.0
    retry_sum = 0

    for chunk in chunks:
        result = _process_chunk(chunk, cfg, translator, proofreader, evaluator, fixer, spellchecker, diff_processor)
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
