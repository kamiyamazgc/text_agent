from .preprocessor import Preprocessor

try:  # Optional dependency
    from .proofreader import Proofreader
except Exception:  # pragma: no cover - optional
    Proofreader = None  # type: ignore

__all__ = ["Preprocessor"]

if Proofreader is not None:
    __all__.append("Proofreader")
