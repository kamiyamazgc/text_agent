import click
from pathlib import Path
from typing import List, Optional
from .config import Config
from .extractors.youtube import YouTubeExtractor
from .extractors.pdf import PDFExtractor
from .extractors.ocr_pdf import OCRPDFExtractor
from .extractors.web import WebExtractor
from .extractors.audio import AudioExtractor
from .processors import Preprocessor
import json
import hashlib
import re

@click.group()
def cli():
    """Document Pipeline System - Convert various document formats to readable Japanese text"""
    pass

@cli.command()
@click.argument("sources", nargs=-1, required=True)
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to config file")
@click.option("--output-dir", "-o", type=click.Path(), help="Output directory")
def process(sources: List[str], config: Optional[str], output_dir: Optional[str]) -> None:
    """Process one or more document sources"""
    cfg = Config.load(config)
    if output_dir:
        cfg.output_dir = Path(output_dir)
    
    # Initialize extractors
    extractors = [
        YouTubeExtractor(cfg.temp_dir),
        WebExtractor(),
        PDFExtractor(),
        OCRPDFExtractor(),
        AudioExtractor(),
        # TODO: Add other extractors
    ]
    preprocessor = Preprocessor()
    
    # Process each source
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
        result["text"] = preprocessor.process(result["text"])

        # Save output
        digest = hashlib.sha1(source.encode("utf-8")).hexdigest()[:8]
        slug = re.sub(r"[^a-zA-Z0-9_-]", "_", source.split("/")[-1])
        output_file = cfg.output_dir / f"doc_{digest}__{slug}.txt"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(result['text'], encoding='utf-8')

        # Save metadata
        meta_file = output_file.with_suffix('.json')
        meta_file.write_text(json.dumps(result['metadata'], indent=2), encoding='utf-8')

        click.echo(f"Successfully processed: {output_file}")

if __name__ == '__main__':
    cli() 
