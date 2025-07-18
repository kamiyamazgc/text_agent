from .preprocessor import Preprocessor
from .fixer import Fixer

try:  # Optional dependency
    from .diff_processor import DiffProcessor
except Exception:  # pragma: no cover - optional
    DiffProcessor = None  # type: ignore

try:  # Optional dependency
    from .translator import Translator
except Exception:  # pragma: no cover - optional
    Translator = None  # type: ignore

try:  # Optional dependency
    from .proofreader import Proofreader
except Exception:  # pragma: no cover - optional
    Proofreader = None  # type: ignore

try:  # Optional dependency
    from .evaluator import Evaluator
except Exception:  # pragma: no cover - optional
    Evaluator = None  # type: ignore

try:  # Optional dependency
    from .spellchecker import SpellChecker
except Exception:  # pragma: no cover - optional
    SpellChecker = None  # type: ignore

__all__ = ["Preprocessor", "Fixer"]

if DiffProcessor is not None:
    __all__.append("DiffProcessor")

if SpellChecker is not None:
    __all__.append("SpellChecker")

if Translator is not None:
    __all__.append("Translator")

if Proofreader is not None:
    __all__.append("Proofreader")

if Evaluator is not None:
    __all__.append("Evaluator")
