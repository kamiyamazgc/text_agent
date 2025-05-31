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

3. Install dependencies:
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

Process with custom configuration:
```bash
python -m docpipe.cli process --config config.yaml --output-dir output/ "input.pdf"
```

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

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 