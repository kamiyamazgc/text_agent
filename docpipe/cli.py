import click
from pathlib import Path
from typing import List, Optional
import json
import re

from .config import Config
from .extractors.youtube import YouTubeExtractor
from .extractors.pdf import PDFExtractor
from .extractors.ocr_pdf import OCRPDFExtractor
from .extractors.ocr_image import OCRImageExtractor
from .extractors.web import WebExtractor
from .extractors.audio import AudioExtractor
from .extractors.plain import PlainTextExtractor
from .processors import (
    Preprocessor,
    Translator,
    Proofreader,
    Evaluator,
    Fixer,
)
from .pipeline import process_text


def _expand_sources(source_paths: List[str]) -> List[str]:
    """Expand directory paths and special files into individual sources."""
    expanded: List[str] = []
    for src in source_paths:
        p = Path(src)
        if p.is_dir():
            for child in p.iterdir():
                if child.is_file():
                    expanded.append(str(child))
        elif p.is_file() and p.name == "urls.txt":
            for line in p.read_text(encoding="utf-8").splitlines():
                url = line.strip()
                if url.lower().startswith("http://") or url.lower().startswith("https://"):
                    expanded.append(url)
        else:
            expanded.append(src)
    return expanded

@click.group()
def cli():
    """Document Pipeline System - Convert various document formats to readable Japanese text"""
    pass

@cli.command()
@click.argument("sources", nargs=-1, required=True)
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to config file")
@click.option("--output-dir", "-o", type=click.Path(), help="Output directory")
def process(sources: List[str], config: Optional[str], output_dir: Optional[str]) -> None:
    """Process one or more document sources.

    Sources can be individual files, URLs, or directories. Directory paths are
    expanded to all files within the directory (non-recursive).
    """
    cfg = Config.load(config)
    if output_dir:
        cfg.output_dir = Path(output_dir)

    sources = _expand_sources(list(sources))
    
    # Initialize extractors
    extractors = [
        YouTubeExtractor(cfg.temp_dir),
        WebExtractor(),
        PDFExtractor(),
        OCRPDFExtractor(),
        OCRImageExtractor(),
        AudioExtractor(cfg.whisper.model),
        PlainTextExtractor(),
        # TODO: Add other extractors
    ]
    preprocessor = Preprocessor()
    translator = Translator(
        cfg.translator.model,
        cfg.translator.temperature,
        cfg.translator.prompt,
    )
    proofreader = Proofreader(
        cfg.proofreader.model,
        cfg.proofreader.style,
        cfg.proofreader.temperature,
        cfg.proofreader.prompt,
    )
    evaluator = Evaluator()
    fixer = Fixer()
    
    # Process each source
    index_counter = 1
    for source in sources:
        click.echo(f"Processing: {source}")

        # Try all extractors that claim they can handle the source
        result = None
        for extractor in [e for e in extractors if e.can_handle(source)]:
            try:
                result = extractor.extract(source)
                break
            except Exception as e:  # pragma: no cover - passthrough errors
                click.echo(
                    f"Extractor {extractor.__class__.__name__} failed: {e}",
                    err=True,
                )

        if result is None:
            click.echo(f"Error: No extractor succeeded for {source}", err=True)
            continue

        # Preprocess text
        text = preprocessor.process(result["text"])

        # Run processing pipeline with quality control
        pipeline_result = process_text(
            text,
            cfg.pipeline,
            translator,
            proofreader,
            evaluator,
            fixer,
        )
        result["text"] = pipeline_result["text"]
        result["metadata"].update(pipeline_result["metadata"])

        # Save output
        slug = re.sub(r"[^a-zA-Z0-9_-]", "_", source.split("/")[-1])
        output_file = cfg.output_dir / f"doc_{index_counter}__{slug}.txt"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(result['text'], encoding='utf-8')

        # Save metadata
        meta_file = output_file.with_suffix('.json')
        meta_file.write_text(json.dumps(result['metadata'], indent=2), encoding='utf-8')

        click.echo(f"Successfully processed: {output_file}")
        index_counter += 1

if __name__ == '__main__':
    cli() 
