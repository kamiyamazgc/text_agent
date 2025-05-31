import click
from pathlib import Path
from typing import List
from .config import Config
from .extractors.youtube import YouTubeExtractor
from .extractors.pdf import PDFExtractor
from .extractors.ocr_pdf import OCRPDFExtractor
import json

@click.group()
def cli():
    """Document Pipeline System - Convert various document formats to readable Japanese text"""
    pass

@cli.command()
@click.argument('sources', nargs=-1, required=True)
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to config file')
@click.option('--output-dir', '-o', type=click.Path(), help='Output directory')
def process(sources: List[str], config: str, output_dir: str):
    """Process one or more document sources"""
    # Load config
    cfg = Config.from_yaml(config) if config else Config()
    if output_dir:
        cfg.output_dir = Path(output_dir)
    
    # Initialize extractors
    extractors = [
        YouTubeExtractor(cfg.temp_dir),
        PDFExtractor(),
        OCRPDFExtractor(),
        # TODO: Add other extractors
    ]
    
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

        # Save output
        output_file = cfg.output_dir / f"doc_{hash(source)}__{source.split('/')[-1]}.txt"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(result['text'], encoding='utf-8')

        # Save metadata
        meta_file = output_file.with_suffix('.json')
        meta_file.write_text(json.dumps(result['metadata'], indent=2), encoding='utf-8')

        click.echo(f"Successfully processed: {output_file}")

if __name__ == '__main__':
    cli() 