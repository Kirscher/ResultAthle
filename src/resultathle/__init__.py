"""ResultAthle - Bases Athle competition scraper and static site generator."""

from importlib.metadata import version, PackageNotFoundError

__all__ = [
    "__version__",
]

try:
    __version__ = version("resultathle")
except PackageNotFoundError:  # pragma: no cover - when running from source
    __version__ = "0.0.0"
