"""Structural Protocols decoupling the linter from concrete adapters.

These Protocols define the contracts the linter expects from its parser,
rule, and configuration-loading collaborators so alternative implementations
can be plugged in without inheritance.
"""

from pathlib import Path
from typing import Protocol

from python_commitlint.core.models import (
    CommitMessage,
    Configuration,
    LintResult,
    RuleConfig,
    ValidationError,
)


class CommitParserProtocol(Protocol):
    """Parses a raw commit message into a :class:`CommitMessage`."""

    def parse(self, message: str) -> CommitMessage:
        """Parse ``message`` and return a structured commit.

        Args:
            message: The raw commit message text, including newlines.

        Returns:
            A :class:`CommitMessage` populated with whichever fields could
            be extracted; non-parseable messages return an empty-typed result.
        """
        ...


class RuleProtocol(Protocol):
    """A single commitlint rule that validates a parsed commit."""

    @property
    def name(self) -> str:
        """The rule's stable identifier (e.g. ``type-case``)."""
        ...

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        """Apply the rule to ``commit`` under the given ``config``.

        Args:
            commit: The parsed commit to validate.
            config: The rule's severity, condition, and optional value.

        Returns:
            A :class:`ValidationError` when the rule is violated, otherwise
            ``None``.
        """
        ...


class ConfigurationLoaderProtocol(Protocol):
    """Loads a :class:`Configuration` from a path or built-in default."""

    def load(self, config_path: Path | None = None) -> Configuration:
        """Load the configuration and return a fully-resolved value.

        Args:
            config_path: Optional explicit path; when ``None`` the loader
                searches the working directory for a default config file.

        Returns:
            The loaded :class:`Configuration`.
        """
        ...


class CommitLinterProtocol(Protocol):
    """Validates a commit message against the configured rule set."""

    def lint(self, message: str) -> LintResult:
        """Validate ``message`` and return the lint outcome.

        Args:
            message: The raw commit message text.

        Returns:
            A :class:`LintResult` containing errors, warnings, and the
            overall ``valid`` flag.
        """
        ...
