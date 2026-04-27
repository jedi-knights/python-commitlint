"""Domain dataclasses — parsed commits, rule configs, and lint results."""

from dataclasses import dataclass, field
from typing import Any

from python_commitlint.core.enums import (
    CaseType,
    RuleCondition,
    Severity,
)


@dataclass(slots=True)
class CommitMessage:
    """A parsed Conventional Commit message.

    For backwards compatibility with consumers that read ``commit.type``
    or ``commit.subject`` directly, those fields default to empty strings
    rather than ``None``. Use :attr:`is_conventional` to distinguish a
    commit that was successfully parsed from one whose header did not
    match the conventional pattern.

    Attributes:
        raw: The original message exactly as provided.
        header: The first line, stripped of trailing whitespace.
        type: The commit type (``feat``, ``fix``, etc.); empty if unparseable.
        scope: The optional scope inside parentheses; empty if unset.
        subject: The text after the ``:`` separator; empty if unparseable.
        body: The body paragraphs (everything between header and footer).
        footer: The footer block (BREAKING CHANGE, ``token: value``, etc.).
        breaking: True when the header has ``!`` or a BREAKING CHANGE footer.
        is_conventional: True when the header matched the conventional
            pattern. False indicates ``type`` / ``scope`` / ``subject``
            were not populated by parsing — empty strings here mean
            "absent", not "explicitly empty".
    """

    raw: str
    header: str
    type: str = ""
    scope: str = ""
    subject: str = ""
    body: str = ""
    footer: str = ""
    breaking: bool = False
    is_conventional: bool = False


@dataclass(slots=True)
class RuleConfig:
    """Per-rule configuration loaded from YAML.

    Attributes:
        severity: How violations are reported (error, warning, disabled).
        condition: Whether the rule must always or never hold.
        value: Rule-specific argument — string, list, int, or None.
    """

    severity: Severity
    condition: RuleCondition
    value: Any = None


@dataclass(slots=True)
class ValidationError:
    """A single rule violation produced by the linter.

    Attributes:
        rule: The rule name (e.g. ``type-case``).
        message: Human-readable explanation of the violation.
        severity: Whether this is an error, warning, or disabled marker.
        line: 1-based line number where the violation was detected.
        column: 0-based column offset; reserved for future use.
    """

    rule: str
    message: str
    severity: Severity
    line: int = 1
    column: int = 0


@dataclass(slots=True)
class LintResult:
    """Outcome of linting a single commit message.

    Attributes:
        valid: True when no errors were produced (warnings do not fail).
        errors: All error-severity violations, in detection order.
        warnings: All warning-severity violations, in detection order.
    """

    valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        """Return True when at least one error-severity violation is present."""
        return bool(self.errors)

    @property
    def has_warnings(self) -> bool:
        """Return True when at least one warning-severity violation is present."""
        return bool(self.warnings)


@dataclass(slots=True)
class Configuration:
    """A fully-resolved commitlint configuration.

    Attributes:
        rules: Mapping of rule name to its :class:`RuleConfig`.
        extends: Names of presets the config inherits from (e.g.
            ``conventional``).
    """

    rules: dict[str, RuleConfig] = field(default_factory=dict)
    extends: list[str] = field(default_factory=list)


@dataclass(slots=True)
class CaseValidation:
    """Dict-form configuration for case rules with custom delimiters.

    Attributes:
        cases: Acceptable case styles to check each split part against.
        delimiters: Characters to split a value on before validating each part.
    """

    cases: list[CaseType]
    delimiters: list[str] = field(default_factory=lambda: ["/", "\\", ","])


@dataclass(slots=True)
class ScopeEnumValidation:
    """Dict-form configuration for ``scope-enum`` with custom delimiters.

    Attributes:
        scopes: Allowed scope values.
        delimiters: Characters to split a multi-scope value on.
    """

    scopes: list[str]
    delimiters: list[str] = field(default_factory=lambda: ["/", "\\", ","])
