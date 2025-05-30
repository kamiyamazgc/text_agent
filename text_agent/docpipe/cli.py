import click
from pathlib import Path
from typing import List
from .config import Config
from .extractors.youtube import YouTubeExtractor
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
        # TODO: Add other extractors
    ]
    
    # Process each source
    for source in sources:
        click.echo(f"Processing: {source}")
        
        # Find appropriate extractor
        extractor = next((e for e in extractors if e.can_handle(source)), None)
        if not extractor:
            click.echo(f"Error: No extractor found for {source}", err=True)
            continue
        
        try:
            # Extract content
            result = extractor.extract(source)
            
            # Save output
            output_file = cfg.output_dir / f"doc_{hash(source)}__{source.split('/')[-1]}.txt"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(result['text'], encoding='utf-8')
            
            # Save metadata
            meta_file = output_file.with_suffix('.json')
            meta_file.write_text(json.dumps(result['metadata'], indent=2), encoding='utf-8')
            
            click.echo(f"Successfully processed: {output_file}")
            
        except Exception as e:
            click.echo(f"Error processing {source}: {str(e)}", err=True)

if __name__ == '__main__':
    cli() 