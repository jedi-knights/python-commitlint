"""Rules that validate the optional scope inside ``type(scope): subject``."""

from python_commitlint.core.enums import CaseType, RuleCondition
from python_commitlint.core.exceptions import ConfigurationError
from python_commitlint.core.models import (
    CaseValidation,
    CommitMessage,
    RuleConfig,
    ScopeEnumValidation,
    ValidationError,
)
from python_commitlint.rules.base import BaseRule
from python_commitlint.rules.case_validators import CaseValidator

_DEFAULT_SCOPE_DELIMITERS = ("/", "\\", ",")


def _split_scope(scope: str, delimiters: list[str]) -> list[str]:
    parts = [scope]
    for delimiter in delimiters:
        new_parts: list[str] = []
        for part in parts:
            new_parts.extend(part.split(delimiter))
        parts = new_parts
    return [p for p in parts if p]


def _build_case_validation(rule_name: str, value: dict) -> CaseValidation:
    try:
        return CaseValidation(**value)
    except TypeError as e:
        raise ConfigurationError(
            f"{rule_name}: invalid case validation config: {e}"
        ) from e


def _build_scope_enum_validation(
    rule_name: str, value: dict
) -> ScopeEnumValidation:
    try:
        return ScopeEnumValidation(**value)
    except TypeError as e:
        raise ConfigurationError(
            f"{rule_name}: invalid scope enum config: {e}"
        ) from e


class ScopeEmptyRule(BaseRule):
    """Require or forbid an empty scope. Rule name: ``scope-empty``."""

    @property
    def name(self) -> str:
        return "scope-empty"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        is_empty = not commit.scope
        should_be_empty = config.condition == RuleCondition.ALWAYS

        if is_empty != should_be_empty:
            msg = (
                "scope may not be empty"
                if not should_be_empty
                else "scope must be empty"
            )
            return self._create_error(config, msg)
        return None


class ScopeCaseRule(BaseRule):
    """Enforce a case style on each scope part. Rule name: ``scope-case``."""

    @property
    def name(self) -> str:
        return "scope-case"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.scope or config.value is None:
            return None

        if isinstance(config.value, dict):
            validation = _build_case_validation(self.name, config.value)
            case_types = validation.cases
            delimiters = validation.delimiters
        else:
            case_types = (
                [CaseType(config.value)]
                if isinstance(config.value, str)
                else [CaseType(v) for v in config.value]
            )
            delimiters = list(_DEFAULT_SCOPE_DELIMITERS)

        scope_parts = _split_scope(commit.scope, delimiters)
        matches_any = all(
            any(
                CaseValidator.validate(part, case_type)
                for case_type in case_types
            )
            for part in scope_parts
        )

        should_match = config.condition == RuleCondition.ALWAYS

        if matches_any != should_match:
            return self._create_error(
                config, f"scope must match case {config.value}"
            )
        return None


class ScopeEnumRule(BaseRule):
    """Restrict scope parts to (or away from) an allowed list. Rule name: ``scope-enum``."""

    @property
    def name(self) -> str:
        return "scope-enum"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.scope:
            return None

        if isinstance(config.value, dict):
            validation = _build_scope_enum_validation(self.name, config.value)
            allowed_scopes = validation.scopes
            delimiters = validation.delimiters
        else:
            allowed_scopes = config.value or []
            delimiters = list(_DEFAULT_SCOPE_DELIMITERS)

        scope_parts = _split_scope(commit.scope, delimiters)
        all_in_enum = all(part in allowed_scopes for part in scope_parts)
        should_be_in_enum = config.condition == RuleCondition.ALWAYS

        if all_in_enum != should_be_in_enum:
            msg = (
                f"scope must be one of {allowed_scopes}"
                if should_be_in_enum
                else f"scope must not be one of {allowed_scopes}"
            )
            return self._create_error(config, msg)
        return None


class ScopeMinLengthRule(BaseRule):
    """Enforce a minimum scope length. Rule name: ``scope-min-length``."""

    @property
    def name(self) -> str:
        return "scope-min-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.scope:
            return None

        min_length = config.value if config.value is not None else 0
        is_valid = len(commit.scope) >= min_length
        should_be_valid = config.condition == RuleCondition.ALWAYS

        if is_valid != should_be_valid:
            return self._create_error(
                config, f"scope must be at least {min_length} characters"
            )
        return None


class ScopeMaxLengthRule(BaseRule):
    """Enforce a maximum scope length. Rule name: ``scope-max-length``."""

    @property
    def name(self) -> str:
        return "scope-max-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.scope:
            return None

        max_length = config.value if config.value is not None else float("inf")
        is_valid = len(commit.scope) <= max_length
        should_be_valid = config.condition == RuleCondition.ALWAYS

        if is_valid != should_be_valid:
            return self._create_error(
                config, f"scope must be at most {max_length} characters"
            )
        return None
