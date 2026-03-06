from python_commitlint.core.enums import CaseType, RuleCondition
from python_commitlint.core.models import (
    CaseValidation,
    CommitMessage,
    RuleConfig,
    ScopeEnumValidation,
    ValidationError,
)
from python_commitlint.rules.base import BaseRule
from python_commitlint.rules.case_validators import CaseValidator


class ScopeEmptyRule(BaseRule):
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
    @property
    def name(self) -> str:
        return "scope-case"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.scope:
            return None

        if isinstance(config.value, dict):
            validation = CaseValidation(**config.value)
            case_types = validation.cases
            delimiters = validation.delimiters
        else:
            case_types = (
                [CaseType(config.value)]
                if isinstance(config.value, str)
                else [CaseType(v) for v in config.value]
            )
            delimiters = ["/", "\\", ","]

        scope_parts = self._split_scope(commit.scope, delimiters)
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

    def _split_scope(self, scope: str, delimiters: list[str]) -> list[str]:
        parts = [scope]
        for delimiter in delimiters:
            new_parts = []
            for part in parts:
                new_parts.extend(part.split(delimiter))
            parts = new_parts
        return [p for p in parts if p]


class ScopeEnumRule(BaseRule):
    @property
    def name(self) -> str:
        return "scope-enum"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.scope:
            return None

        if isinstance(config.value, dict):
            validation = ScopeEnumValidation(**config.value)
            allowed_scopes = validation.scopes
            delimiters = validation.delimiters
        else:
            allowed_scopes = config.value or []
            delimiters = ["/", "\\", ","]

        scope_parts = self._split_scope(commit.scope, delimiters)
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

    def _split_scope(self, scope: str, delimiters: list[str]) -> list[str]:
        parts = [scope]
        for delimiter in delimiters:
            new_parts = []
            for part in parts:
                new_parts.extend(part.split(delimiter))
            parts = new_parts
        return [p for p in parts if p]


class ScopeMinLengthRule(BaseRule):
    @property
    def name(self) -> str:
        return "scope-min-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.scope:
            return None

        min_length = config.value or 0
        is_valid = len(commit.scope) >= min_length
        should_be_valid = config.condition == RuleCondition.ALWAYS

        if is_valid != should_be_valid:
            return self._create_error(
                config, f"scope must be at least {min_length} characters"
            )
        return None


class ScopeMaxLengthRule(BaseRule):
    @property
    def name(self) -> str:
        return "scope-max-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.scope:
            return None

        max_length = config.value or float("inf")
        is_valid = len(commit.scope) <= max_length
        should_be_valid = config.condition == RuleCondition.ALWAYS

        if is_valid != should_be_valid:
            return self._create_error(
                config, f"scope must be at most {max_length} characters"
            )
        return None
