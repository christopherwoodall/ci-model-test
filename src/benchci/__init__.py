# ruff: noqa: F401
# Configure clean imports for the package
# See: https://hynek.me/articles/testing-packaging/

from . import evaluation
from .evaluation import run_evaluation, load_config

__all__ = ["evaluation", "run_evaluation", "load_config"]
