# Text Agent - Document Pipeline System

A unified document conversion framework that transforms various input sources into high-quality, readable Japanese text with intelligent quality control and retry mechanisms.

## Features

### Supported Input Formats
- **PDF Documents**: Digital PDFs with text extraction
- **Audio Files**: MP3, WAV, M4A with Whisper transcription
- **Web Pages**: Automatic content extraction with trafilatura
- **YouTube Videos**: Automatic subtitle extraction with audio fallback
- **Images**: OCR processing with Tesseract (PNG, JPG)
- **Plain Text**: TXT and Markdown files

### Quality Assurance & Processing
- **Intelligent Translation**: Multi-language to Japanese translation (translator returns only the translated text)
- **Grammar Checking**: LanguageTool integration for error detection. Proofreader keeps the original meaning, leaves unknown terms untouched, and outputs only the corrected text.
- **Readability Scoring**: LLM-based quality evaluation
- **Automatic Retry**: Smart retry logic for quality improvement
- **Text Fixing**: Mechanical fixes for common transcription errors
- **Spell Checking**: Optional spell correction for obvious errors
- **Speech Recognition Error Correction**: Specialized fixes for audio transcription artifacts

### Output Features
- **Smart Filenames**: YYYYMMDD format with meaningful names from metadata
- **Metadata Preservation**: JSON metadata files with processing details
- **Quality Metrics**: Comprehensive scoring and evaluation data

## Installation

### Method 1: Package Installation (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/kamiyamazgc/text_agent.git
cd text_agent
```

2. Create and activate a virtual environment:
```bash
python -m venv venv311
source venv311/bin/activate  # On Windows: venv311\Scripts\activate
```

3. Install the package in development mode:
```bash
pip install -e .
```

4. Set up environment variables:
```bash
# Create .env file with your API keys
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

### Method 2: Direct Installation

1. Clone and setup as above, then install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

The system provides a `text-agent` command (when installed as package) or can be run directly:

#### Process Single Document
```bash
# Using package command
text-agent process "path/to/document.pdf"

# Using direct execution
python -m docpipe.cli process "path/to/document.pdf"
```

#### Process Multiple Sources
```bash
text-agent process "doc1.pdf" "audio.mp3" "https://youtube.com/watch?v=..."
```

#### Process Directory Contents
```bash
text-agent process path/to/folder/
```

#### Process URLs from File
```bash
text-agent process urls.txt
```
Each line of `urls.txt` should contain a web page URL. Lines that don't start with `http://` or `https://` are ignored.

#### Custom Output Directory
```bash
text-agent process --output-dir output/ "input.pdf"
```

### Output File Naming

Files are saved with the format:
`{YYMMDD}_{sequence:03d}_{meaningful_name}{output_extension}`

Examples:
- `250115_001_OpenAI_GPT4_1_発表.md`
- `250115_002_YouTube動画の文字起こし.md`
- `250115_003_技術文書.md`

Set `output_extension` in `config.yaml` to change the extension (e.g. `.txt`).

The meaningful name is extracted from metadata in this priority order:
1. Title from source
2. Description (first 50 characters)
3. Original filename
4. Fallback to sanitized source name

## Configuration

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
  model: "gpt-4.1-mini"
  temperature: 0.7

translator:
  model: "gpt-4"
  temperature: 0.7
  prompt: "Translate the following text to {target_lang}:\n{text}\n翻訳結果のみを返してください。"

proofreader:
  model: "gpt-4o"
  style: "general"
  temperature: 0.0
  enabled: true
  prompt: "Proofread the following text. Fix grammar, style, and readability issues in {style} style. 文の意味を変えないこと。未知の用語はそのまま残すこと。結果だけを出力してください。"

whisper:
  model: "large"
  language:  # Optional: force transcription language

output_dir: "output"
temp_dir: "temp"
log_dir: "logs"
output_extension: ".md"
```

### Configuration Options

- **pipeline**: Quality control parameters
  - `quality_threshold`: Minimum quality score to stop retrying
  - `max_retries`: Maximum number of retry attempts
  - `min_improvement`: Minimum improvement required to continue retrying
  - `language_tool_threshold`: Maximum grammar error rate
  - `bleu_threshold`: Minimum BLEU score for translations

- **llm**: Shared LLM settings
  - `profile`: API profile (`default` or `local`)
  - `model`: Model name
  - `temperature`: Sampling temperature

- **translator**: Translation step settings
- **proofreader**: Proofreading step settings (`enabled` to skip)
- **whisper**: Audio transcription options

## Processing Pipeline

The system follows this intelligent processing flow:

1. **Extraction**: Detect format and extract content using appropriate extractor
2. **Preprocessing**: Clean and normalize text
3. **Translation**: Convert to Japanese if needed
4. **Proofreading**: Grammar and style correction
5. **Quality Evaluation**: Score readability and grammar
6. **Retry Logic**: Automatically retry with improvements if quality is low
7. **Text Fixing**: Apply mechanical fixes for common errors
8. **Output**: Save with smart filename and metadata

### Quality Control Features

- **Intelligent Retry**: Continues retries until quality threshold is met or max retries reached
- **Speech Error Correction**: Specialized fixes for Whisper transcription artifacts
- **Python Code Preservation**: Maintains syntax when processing code files
- **Metadata Enhancement**: Enriches output with processing details

## Development

### Project Structure

```
text_agent/
├── docpipe/
│   ├── cli.py              # Command line interface
│   ├── config.py           # Configuration management
│   ├── pipeline.py         # Main processing pipeline
│   │   ├── base.py
│   │   ├── pdf.py
│   │   ├── audio.py
│   │   ├── web.py
│   │   ├── youtube.py
│   │   ├── ocr_image.py
│   │   └── plain.py
│   ├── processors/         # Text processing components
│   │   ├── preprocessor.py
│   │   ├── translator.py
│   │   ├── proofreader.py
│   │   ├── evaluator.py
│   │   ├── fixer.py
│   │   └── spellchecker.py (optional)
│   └── tests/              # Test suite
├── config.yaml             # Default configuration
├── requirements.txt        # Dependencies
└── setup.py               # Package configuration
```

### Adding New Extractors

1. Create a new extractor class in `extractors/` that inherits from `BaseExtractor`
2. Implement required methods:
   - `can_handle(source: str) -> bool`
   - `extract(source: str, **kwargs) -> Dict[str, Any]`
3. Register the extractor in `cli.py`

### Running Tests

```bash
pytest docpipe/tests/
```

## Requirements

- Python 3.11+
- OpenAI API key (for LLM features)
- Java (for LanguageTool)
- Tesseract (for OCR features)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Recent Updates

- **Smart Filename Generation**: YYYYMMDD format with metadata-based names
- **Enhanced Retry Logic**: Improved quality control with better retry strategies
- **Speech Error Correction**: Specialized fixes for audio transcription
- **Python Code Preservation**: Maintains syntax integrity for code files
- **Spell Checker Integration**: Optional spell correction for obvious errors
- **Package Installation**: Easy global installation with `pip install -e .`
