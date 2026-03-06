from dataclasses import dataclass, field
from typing import Any

from python_commitlint.enums import (
    CaseType,
    RuleCondition,
    Severity,
)


@dataclass
class CommitMessage:
    raw: str
    header: str
    type: str = ""
    scope: str = ""
    subject: str = ""
    body: str = ""
    footer: str = ""
    breaking: bool = False


@dataclass
class RuleConfig:
    severity: Severity
    condition: RuleCondition
    value: Any = None


@dataclass
class ValidationError:
    rule: str
    message: str
    severity: Severity
    line: int = 1
    column: int = 0


@dataclass
class LintResult:
    valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0


@dataclass
class Configuration:
    rules: dict[str, RuleConfig] = field(default_factory=dict)
    extends: list[str] = field(default_factory=list)


@dataclass
class CaseValidation:
    cases: list[CaseType]
    delimiters: list[str] = field(default_factory=lambda: ["/", "\\", ","])


@dataclass
class ScopeEnumValidation:
    scopes: list[str]
    delimiters: list[str] = field(default_factory=lambda: ["/", "\\", ","])
