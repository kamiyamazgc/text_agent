# Codebase Summary

**Notes**

- `docpipe/cli.py` loads the glossary twice. The second initialization overwrites the instance used for the translator and proofreader, causing unnecessary re-loading. Lines 78-83 and 99-104 show the duplicated block.

:::task-stub{title="Avoid redundant Glossary loading in CLI"}
1. In `docpipe/cli.py`, remove lines that reset and re-load the glossary (currently around lines 99-104).
2. Pass the originally created `glossary` instance to the `Fixer` so all processors share one object.
3. Ensure unit tests still pass (`pytest docpipe/tests`).

Search keywords: "glossary = None" in `cli.py`.
:::

**Summary**

The project implements a document processing pipeline that converts many input types to polished Japanese text. The overall agent flow is documented in `AGENTS.md`, which shows extractors feeding into preprocess, translation, proofreading, evaluation, and fixing with retries until quality is acceptable.

Configuration defaults are defined in `config.yaml` with options for pipeline thresholds, translator and proofreader models, and output settings. The CLI (`docpipe/cli.py`) reads this configuration, expands provided paths or URLs, and initializes extractors for YouTube, web pages, PDFs, images, audio, and plain text. Each source is processed through preprocessing and the main pipeline, then saved with a meaningful timestamped filename.

The main processing logic resides in `pipeline.py`. Text is optionally split into token chunks and each chunk undergoes translation, optional proofreading, and evaluation. Quality control applies language-tool and BLEU thresholds; if quality is low, a fixer is run and the loop may retry until the threshold or max retries is reached. A spell-checker runs only if the final quality remains below a set value.

Individual extractors handle specific formats: PDF via marker-pdf or PyPDFium2, OCR PDF via marker-ocr-pdf, audio using Whisper, web pages through trafilatura, images via Tesseract OCR, and YouTube using yt-dlp with caption or audio fallback. Each returns text plus metadata about the source.

Processors provide translation (OpenAI API with glossary support), proofreading, evaluation (language-tool, readability scoring, BLEU), fixing of common errors, and a basic spell checker. The glossary class can load CSV or YAML files and replace terms accordingly.

Extensive tests under `docpipe/tests` cover extractors, processors, configuration loading, and pipeline behavior. The README outlines usage and development instructions, including optional dependencies for advanced features, and summarises the supported formats and quality control mechanisms.

Overall the system provides a flexible pipeline for transforming diverse documents into Japanese text with automated quality assurance and retry logic. The architecture allows adding new extractors or processors as needed, with configuration driven by YAML settings.

