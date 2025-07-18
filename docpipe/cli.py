import click
from pathlib import Path
from typing import List, Optional
from itertools import chain
import json
import re
from datetime import datetime
import logging

from .config import Config
from .extractors.youtube import YouTubeExtractor
from .extractors.pdf import PDFExtractor
from .extractors.ocr_image import OCRImageExtractor
from .extractors.web import WebExtractor
from .extractors.audio import AudioExtractor
from .extractors.plain import PlainTextExtractor
from .glossary import Glossary
from .processors import (
    Preprocessor,
    Translator,
    Proofreader,
    Evaluator,
    Fixer,
    SpellChecker,
    DiffProcessor,
)
from .pipeline import process_text


def _expand_sources(source_paths: List[str]) -> List[str]:
    """Expand directory paths and special files into individual sources."""

    def expand(src: str) -> List[str]:
        p = Path(src)
        if p.is_dir():
            return [str(c) for c in p.iterdir() if c.is_file()]
        if p.is_file() and p.name == "urls.txt":
            return [
                line.strip()
                for line in p.read_text(encoding="utf-8").splitlines()
                if line.strip().startswith(("http://", "https://"))
            ]
        return [src]

    return list(chain.from_iterable(expand(s) for s in source_paths))

@click.group()
def cli():
    """Document Pipeline System - Convert various document formats to readable Japanese text"""
    pass

@cli.command()
@click.argument("sources", nargs=-1, required=True)
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to config file")
@click.option("--output-dir", "-o", type=click.Path(), help="Output directory")
@click.option("--log-level", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]), help="Logging level")
def process(sources: List[str], config: Optional[str], output_dir: Optional[str], log_level: Optional[str]) -> None:
    """Process one or more document sources.

    Sources can be individual files, URLs, or directories. Directory paths are
    expanded to all files within the directory (non-recursive).
    """
    cfg = Config.load(config)
    if output_dir:
        cfg.output_dir = Path(output_dir)
    if log_level:
        cfg.log_level = log_level
    logging.basicConfig(level=getattr(logging, cfg.log_level.upper(), logging.INFO))

    sources = _expand_sources(list(sources))
    
    # Initialize extractors
    extractors = [
        YouTubeExtractor(cfg.temp_dir),
        WebExtractor(),
        PDFExtractor(),
        # OCRPDFExtractor(),  # Temporarily disabled due to missing marker-ocr-pdf
        OCRImageExtractor(),
        AudioExtractor(cfg.whisper.model),
        PlainTextExtractor(),
        # TODO: Add other extractors
    ]
    preprocessor = Preprocessor()
    glossary = None
    if cfg.glossary.enabled and cfg.glossary.path:
        try:
            glossary = Glossary(str(cfg.glossary.path))
        except Exception as exc:  # pragma: no cover - CLI only
            click.echo(f"Failed to load glossary: {exc}")
    translator = Translator(
        cfg.translator.model,
        cfg.translator.temperature,
        cfg.translator.prompt,
        glossary=glossary,
    )
    proofreader = Proofreader(
        cfg.proofreader.model,
        cfg.proofreader.style,
        cfg.proofreader.temperature,
        cfg.proofreader.prompt,
        glossary=glossary,
    )
    evaluator = Evaluator()

    fixer = Fixer(cfg.enable_markdown_headings, glossary=glossary)
    spellchecker = SpellChecker()
    
    # Process each source
    index_counter = 1
    with click.progressbar(sources, label="Processing sources") as bar:
        for source in bar:
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

            # Generate meaningful filename using metadata and yymmdd format
            timestamp = datetime.now().strftime("%y%m%d")

            # Try to get meaningful name from metadata
            meaningful_name = None
            if "title" in result["metadata"] and result["metadata"]["title"]:
                meaningful_name = result["metadata"]["title"]
            elif "description" in result["metadata"] and result["metadata"]["description"]:
                # Use first 50 chars of description if title not available
                meaningful_name = result["metadata"]["description"][:50]
            elif "filename" in result["metadata"] and result["metadata"]["filename"]:
                meaningful_name = result["metadata"]["filename"]

            if meaningful_name:
                # Clean the meaningful name for filename use
                meaningful_name = re.sub(r"[^a-zA-Z0-9_\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]", "_", meaningful_name)
                meaningful_name = meaningful_name.strip("_")
                # Limit length to avoid too long filenames
                if len(meaningful_name) > 50:
                    meaningful_name = meaningful_name[:50].rstrip("_")
            else:
                # Fallback to source-based slug
                meaningful_name = re.sub(r"[^a-zA-Z0-9_-]", "_", source.split("/")[-1])

            # Create case-specific directory
            case_dir = cfg.output_dir / f"{timestamp}_{index_counter:03d}_{meaningful_name}"
            case_dir.mkdir(parents=True, exist_ok=True)
            
            # Create temp subdirectory for intermediate files
            temp_dir = case_dir / "temp"
            temp_dir.mkdir(exist_ok=True)

            # Save original files based on source type
            source_type = result["metadata"].get("source_type", "unknown")
            
            if source_type == "pdf":
                # Save original PDF if available
                if "file_name" in result["metadata"]:
                    pdf_source = Path(source)
                    if pdf_source.exists():
                        pdf_dest = case_dir / "original.pdf"
                        import shutil
                        shutil.copy2(pdf_source, pdf_dest)
                
                # Save extracted text as original.txt
                original_txt = case_dir / "original.txt"
                original_txt.write_text(result["text"], encoding='utf-8')
                
                # If marker was used, save as original.md and copy images
                if result["metadata"].get("extractor") == "marker":
                    original_md = case_dir / "original.md"
                    original_md.write_text(result["text"], encoding='utf-8')
                    
                    # Copy image files if available
                    if "image_files" in result["metadata"] and "marker_output_dir" in result["metadata"]:
                        marker_output_dir = Path(result["metadata"]["marker_output_dir"])
                        image_files = result["metadata"]["image_files"]
                        
                        print(f"DEBUG: Copying {len(image_files)} image files to case directory")
                        for image_path in image_files:
                            image_source = Path(image_path)
                            if image_source.exists():
                                image_dest = case_dir / image_source.name
                                import shutil
                                shutil.copy2(image_source, image_dest)
                                print(f"DEBUG: Copied {image_source.name} to {image_dest}")
                            else:
                                print(f"DEBUG: Image file not found: {image_path}")
                    
            elif source_type in ["web", "youtube"]:
                # Save extracted text as original.txt
                original_txt = case_dir / "original.txt"
                original_txt.write_text(result["text"], encoding='utf-8')
                
            else:
                # For other source types, save as original.txt
                original_txt = case_dir / "original.txt"
                original_txt.write_text(result["text"], encoding='utf-8')

            # Save metadata
            meta_file = case_dir / "metadata.json"
            meta_file.write_text(json.dumps(result["metadata"], indent=2), encoding='utf-8')
            
            click.echo(f"Saved original files to: {case_dir}")

            # Initialize DiffProcessor with case-specific temp directory
            diff_processor = None
            if cfg.diff_processor.enabled:
                try:
                    diff_processor = DiffProcessor(
                        model=cfg.diff_processor.model,
                        max_chunk_size=cfg.diff_processor.max_chunk_size,
                        max_retries=cfg.diff_processor.max_retries,
                        output_history=cfg.diff_processor.output_history,
                        history_dir=cfg.diff_processor.history_dir,
                        improvement_focus=cfg.diff_processor.improvement_focus,
                        temp_dir=str(temp_dir),  # Pass case-specific temp directory
                    )
                    click.echo("DiffProcessor initialized successfully")
                except Exception as e:
                    click.echo(f"Failed to initialize DiffProcessor: {e}", err=True)

            # Run processing pipeline with quality control
            pipeline_result = process_text(
                text,
                cfg,
                translator,
                proofreader,
                evaluator,
                fixer,
                spellchecker,
                diff_processor,
            )
            result["text"] = pipeline_result["text"]
            result["metadata"].update(pipeline_result["metadata"])

            # Save final processed text
            final_file = case_dir / "final.md"
            final_file.write_text(result['text'], encoding='utf-8')

            # Save final metadata
            final_meta_file = case_dir / "final_metadata.json"
            final_meta_file.write_text(json.dumps(result['metadata'], indent=2), encoding='utf-8')

            click.echo(f"Successfully processed: {final_file}")
            index_counter += 1

if __name__ == '__main__':
    cli() 
