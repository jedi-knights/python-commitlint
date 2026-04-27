"""python-commitlint — pure-Python validator for Conventional Commits.

This package exposes the public API for linting commit messages and for
converting legacy ``commitlint.config.js`` files into ``.commitlintrc.yaml``.

Most users only need:

- :class:`CommitLinterFactory` to construct a linter (with optional config path)
- :class:`LintResult` and :class:`ValidationError` for inspecting results
- :class:`CommitMessage` if writing custom rules or callbacks
- :class:`ConfigurationError` to handle config-loading failures
- :func:`convert_js_to_yaml` for one-shot JS-to-YAML config conversion
"""

from python_commitlint.config.converter import (
    CommitlintConfigConverter,
    convert_js_to_yaml,
)
from python_commitlint.core.exceptions import ConfigurationError
from python_commitlint.core.models import (
    CommitMessage,
    LintResult,
    ValidationError,
)
from python_commitlint.linter import CommitLinterFactory

__all__ = [
    "CommitLinterFactory",
    "CommitMessage",
    "CommitlintConfigConverter",
    "ConfigurationError",
    "LintResult",
    "ValidationError",
    "convert_js_to_yaml",
]
