"""Core domain layer — enums, dataclasses, protocols, and exceptions.

This subpackage holds the framework-free building blocks used throughout
python-commitlint: shared enumerations, validated value objects, structural
Protocol contracts for adapters, and the :class:`ConfigurationError` raised
at the configuration boundary.
"""

from python_commitlint.core.enums import (
    CaseType,
    RuleCondition,
    Severity,
)
from python_commitlint.core.exceptions import ConfigurationError
from python_commitlint.core.models import (
    CaseValidation,
    CommitMessage,
    Configuration,
    LintResult,
    RuleConfig,
    ScopeEnumValidation,
    ValidationError,
)
from python_commitlint.core.protocols import (
    CommitLinterProtocol,
    CommitParserProtocol,
    ConfigurationLoaderProtocol,
    RuleProtocol,
)

__all__ = [
    "CaseType",
    "CaseValidation",
    "CommitLinterProtocol",
    "CommitMessage",
    "CommitParserProtocol",
    "Configuration",
    "ConfigurationError",
    "ConfigurationLoaderProtocol",
    "LintResult",
    "RuleCondition",
    "RuleConfig",
    "RuleProtocol",
    "ScopeEnumValidation",
    "Severity",
    "ValidationError",
]
