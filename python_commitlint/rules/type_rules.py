from python_commitlint.case_validators import CaseValidator
from python_commitlint.enums import CaseType, RuleCondition
from python_commitlint.models import (
    CommitMessage,
    RuleConfig,
    ValidationError,
)
from python_commitlint.rules.base import BaseRule


class TypeEmptyRule(BaseRule):
    @property
    def name(self) -> str:
        return "type-empty"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        is_empty = not commit.type
        should_be_empty = config.condition == RuleCondition.ALWAYS

        if is_empty != should_be_empty:
            msg = (
                "type may not be empty"
                if not should_be_empty
                else "type must be empty"
            )
            return self._create_error(config, msg)
        return None


class TypeCaseRule(BaseRule):
    @property
    def name(self) -> str:
        return "type-case"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.type:
            return None

        case_type = CaseType(config.value)
        is_valid = CaseValidator.validate(commit.type, case_type)
        should_match = config.condition == RuleCondition.ALWAYS

        if is_valid != should_match:
            return self._create_error(config, f"type must be {config.value}")
        return None


class TypeEnumRule(BaseRule):
    @property
    def name(self) -> str:
        return "type-enum"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.type:
            return None

        allowed_types = config.value or []
        is_in_enum = commit.type in allowed_types
        should_be_in_enum = config.condition == RuleCondition.ALWAYS

        if is_in_enum != should_be_in_enum:
            msg = (
                f"type must be one of {allowed_types}"
                if should_be_in_enum
                else f"type must not be one of {allowed_types}"
            )
            return self._create_error(config, msg)
        return None


class TypeMinLengthRule(BaseRule):
    @property
    def name(self) -> str:
        return "type-min-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.type:
            return None

        min_length = config.value or 0
        is_valid = len(commit.type) >= min_length
        should_be_valid = config.condition == RuleCondition.ALWAYS

        if is_valid != should_be_valid:
            return self._create_error(
                config, f"type must be at least {min_length} characters"
            )
        return None


class TypeMaxLengthRule(BaseRule):
    @property
    def name(self) -> str:
        return "type-max-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.type:
            return None

        max_length = config.value or float("inf")
        is_valid = len(commit.type) <= max_length
        should_be_valid = config.condition == RuleCondition.ALWAYS

        if is_valid != should_be_valid:
            return self._create_error(
                config, f"type must be at most {max_length} characters"
            )
        return None
