from .preprocessor import Preprocessor
from .fixer import Fixer

try:  # Optional dependency
    from .translator import Translator
except Exception:  # pragma: no cover - optional
    Translator = None  # type: ignore

try:  # Optional dependency
    from .evaluator import Evaluator
except Exception:  # pragma: no cover - optional
    Evaluator = None  # type: ignore

try:  # Optional dependency
    from .proofreader import Proofreader
except Exception:  # pragma: no cover - optional
    Proofreader = None  # type: ignore

__all__ = ["Preprocessor", "Fixer"]

if Translator is not None:
    __all__.append("Translator")

if Proofreader is not None:
    __all__.append("Proofreader")

if Evaluator is not None:
    __all__.append("Evaluator")

