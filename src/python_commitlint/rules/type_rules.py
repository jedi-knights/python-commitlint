"""Rules that validate the commit ``type`` (the token before the colon)."""

from python_commitlint.core.enums import CaseType, RuleCondition
from python_commitlint.core.exceptions import ConfigurationError
from python_commitlint.core.models import (
    CommitMessage,
    RuleConfig,
    ValidationError,
)
from python_commitlint.rules.base import BaseRule, config_value_or
from python_commitlint.rules.case_validators import CaseValidator


class TypeEmptyRule(BaseRule):
    """Require or forbid an empty type. Rule name: ``type-empty``."""

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
    """Enforce a single case style on the type. Rule name: ``type-case``."""

    @property
    def name(self) -> str:
        return "type-case"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.type or config.value is None:
            return None

        case_type = CaseType(config.value)
        is_valid = CaseValidator.validate(commit.type, case_type)
        should_match = config.condition == RuleCondition.ALWAYS

        if is_valid != should_match:
            return self._create_error(config, f"type must be {config.value}")
        return None


class TypeEnumRule(BaseRule):
    """Restrict the type to (or away from) an allowed list. Rule name: ``type-enum``."""

    @property
    def name(self) -> str:
        return "type-enum"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.type:
            return None

        if config.value is None:
            raise ConfigurationError(
                f"{self.name}: requires a 'value' (list of allowed types)"
            )
        allowed_types = config.value
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
    """Enforce a minimum character length on the type. Rule name: ``type-min-length``."""

    @property
    def name(self) -> str:
        return "type-min-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.type:
            return None

        min_length = config_value_or(config, 0)
        is_valid = len(commit.type) >= min_length
        should_be_valid = config.condition == RuleCondition.ALWAYS

        if is_valid != should_be_valid:
            return self._create_error(
                config, f"type must be at least {min_length} characters"
            )
        return None


class TypeMaxLengthRule(BaseRule):
    """Enforce a maximum character length on the type. Rule name: ``type-max-length``."""

    @property
    def name(self) -> str:
        return "type-max-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.type:
            return None

        max_length = config_value_or(config, float("inf"))
        is_valid = len(commit.type) <= max_length
        should_be_valid = config.condition == RuleCondition.ALWAYS

        if is_valid != should_be_valid:
            return self._create_error(
                config, f"type must be at most {max_length} characters"
            )
        return None
