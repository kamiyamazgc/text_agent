from .preprocessor import Preprocessor

try:  # Optional dependency
    from .evaluator import Evaluator
except Exception:  # pragma: no cover - optional
    Evaluator = None  # type: ignore

try:  # Optional dependency
    from .proofreader import Proofreader
except Exception:  # pragma: no cover - optional
    Proofreader = None  # type: ignore

__all__ = ["Preprocessor"]

if Proofreader is not None:
    __all__.append("Proofreader")

if Evaluator is not None:
    __all__.append("Evaluator")

