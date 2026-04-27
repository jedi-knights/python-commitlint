"""Rules that validate the entire header line (``type(scope): subject``)."""

from python_commitlint.core.enums import CaseType, RuleCondition
from python_commitlint.core.models import (
    CommitMessage,
    RuleConfig,
    ValidationError,
)
from python_commitlint.rules.base import BaseRule
from python_commitlint.rules.case_validators import CaseValidator


class HeaderMaxLengthRule(BaseRule):
    """Enforce a maximum header length. Rule name: ``header-max-length``."""

    @property
    def name(self) -> str:
        return "header-max-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        max_length = config.value if config.value is not None else float("inf")
        is_valid = len(commit.header) <= max_length
        should_be_valid = config.condition == RuleCondition.ALWAYS

        if is_valid != should_be_valid:
            return self._create_error(
                config, f"header must be at most {max_length} characters"
            )
        return None


class HeaderMinLengthRule(BaseRule):
    """Enforce a minimum header length. Rule name: ``header-min-length``."""

    @property
    def name(self) -> str:
        return "header-min-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        min_length = config.value if config.value is not None else 0
        is_valid = len(commit.header) >= min_length
        should_be_valid = config.condition == RuleCondition.ALWAYS

        if is_valid != should_be_valid:
            return self._create_error(
                config, f"header must be at least {min_length} characters"
            )
        return None


class HeaderTrimRule(BaseRule):
    """Forbid leading or trailing whitespace on the header. Rule name: ``header-trim``."""

    @property
    def name(self) -> str:
        return "header-trim"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        is_trimmed = commit.header == commit.header.strip()
        should_be_trimmed = config.condition == RuleCondition.ALWAYS

        if is_trimmed != should_be_trimmed:
            return self._create_error(
                config, "header must not have leading or trailing whitespace"
            )
        return None


class HeaderFullStopRule(BaseRule):
    """Require or forbid a trailing punctuation character. Rule name: ``header-full-stop``."""

    @property
    def name(self) -> str:
        return "header-full-stop"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.header:
            return None

        stop_char = config.value if config.value is not None else "."
        ends_with_stop = commit.header.endswith(stop_char)
        should_end_with_stop = config.condition == RuleCondition.ALWAYS

        if ends_with_stop != should_end_with_stop:
            msg = (
                f"header must end with '{stop_char}'"
                if should_end_with_stop
                else f"header may not end with '{stop_char}'"
            )
            return self._create_error(config, msg)
        return None


class HeaderCaseRule(BaseRule):
    """Enforce a case style on the full header. Rule name: ``header-case``."""

    @property
    def name(self) -> str:
        return "header-case"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.header or config.value is None:
            return None

        case_types = (
            config.value if isinstance(config.value, list) else [config.value]
        )

        matches_any = any(
            CaseValidator.validate(commit.header, CaseType(case_type))
            for case_type in case_types
        )

        should_match = config.condition == RuleCondition.ALWAYS

        if matches_any != should_match:
            return self._create_error(
                config, f"header must match case {config.value}"
            )
        return None
