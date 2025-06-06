# Document Pipeline System

A unified document conversion framework that transforms various input sources into high-quality, readable Japanese text.

## Features

- Support for multiple input formats:
  - PDF (digital) and scanned PDFs via OCR
  - Audio files (MP3, WAV, M4A)
  - Web pages
  - YouTube videos (with automatic caption extraction)
  - Images (coming soon)
  - Plain text and Markdown

- Quality assurance:
  - Automatic grammar checking
  - Readability scoring
  - Translation quality metrics
  - Retry mechanism for low-quality outputs

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/docpipe.git
cd docpipe
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies (the CLI uses the `click` package):
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Process a single document:
```bash
python -m docpipe.cli process "path/to/document.pdf"
```

Process multiple documents:
```bash
python -m docpipe.cli process "doc1.pdf" "doc2.mp3" "https://youtube.com/watch?v=..."
```

Process all files in a folder (non-recursive):
```bash
python -m docpipe.cli process path/to/folder/
```

Process URLs listed in `urls.txt`:
```bash
python -m docpipe.cli process urls.txt
```
Each line of `urls.txt` should contain a web page URL. Lines that do not start
with `http://` or `https://` are ignored.

Process with custom configuration (reads `config.yaml` automatically):
```bash
python -m docpipe.cli process --output-dir output/ "input.pdf"
```
You can specify a different file with `--config path/to/file.yaml`.

### Configuration

Create a `config.yaml` file to customize the pipeline:

```yaml
pipeline:
  quality_threshold: 0.85
  max_retries: 3
  min_improvement: 0.01
  language_tool_threshold: 0.02
  bleu_threshold: 35.0

llm:
  profile: "default"  # or "local"
  model: "gpt-4"
  temperature: 0.7

output_dir: "output"
temp_dir: "temp"
log_dir: "logs"
```
The available keys are shown below. Any field omitted will fall back to the
defaults defined in `docpipe.config.Config`.

* `pipeline` &ndash; Parameters that control quality checking and retries
  * `quality_threshold` &ndash; minimum quality score to stop retrying
  * `max_retries` &ndash; maximum number of retry attempts
  * `min_improvement` &ndash; minimum improvement required to continue retrying
  * `language_tool_threshold` &ndash; maximum grammar error rate
  * `bleu_threshold` &ndash; minimum BLEU score for translations
* `llm` &ndash; Shared settings for LLM access
  * `profile` &ndash; API profile (`default` or `local`)
  * `model` &ndash; model name
  * `temperature` &ndash; sampling temperature
* `translator` &ndash; Settings used in the translation step
  * `model` &ndash; model name
  * `temperature` &ndash; sampling temperature
  * `prompt` &ndash; custom translation prompt
* `proofreader` &ndash; Settings for the proofreader step
  * `model` &ndash; model name
  * `style` &ndash; proofreading style
  * `temperature` &ndash; sampling temperature
  * `prompt` &ndash; custom proofreading prompt
* `whisper` &ndash; Options for audio transcription
  * `model` &ndash; Whisper model name
  * `language` &ndash; force transcription language (optional)
* `output_dir` &ndash; directory for processed text
* `temp_dir` &ndash; directory for temporary files
* `log_dir` &ndash; directory for logs

This file will be loaded automatically when running the CLI from the same directory.

#### Configuration Precedence

Configuration is resolved in this order:

1. **Command line options** such as `--output-dir` and `--config` take highest priority.
2. If `--config` is not provided but `config.yaml` exists in the current directory, it is loaded.
3. Otherwise, default values defined in `docpipe.config.Config` are used.

All configuration is loaded via `Config.load()` so the rule is consistent across the project.

## Development

### Project Structure

```
docpipe/
├── __init__.py
├── config.py
├── cli.py
├── extractors/
│   ├── __init__.py
│   ├── base.py
│   ├── youtube.py
│   └── ...
└── tests/
    └── ...
```

### Adding New Extractors

1. Create a new extractor class in `extractors/` that inherits from `BaseExtractor`
2. Implement the required methods:
   - `can_handle(source: str) -> bool`
   - `extract(source: str, **kwargs) -> Dict[str, Any]`
3. Register the extractor in `cli.py`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
