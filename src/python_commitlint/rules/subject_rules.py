"""Rules that validate the subject (the text after ``type(scope):``)."""

from python_commitlint.core.enums import CaseType, RuleCondition
from python_commitlint.core.models import (
    CommitMessage,
    RuleConfig,
    ValidationError,
)
from python_commitlint.rules.base import BaseRule
from python_commitlint.rules.case_validators import CaseValidator


class SubjectEmptyRule(BaseRule):
    """Require or forbid an empty subject. Rule name: ``subject-empty``."""

    @property
    def name(self) -> str:
        return "subject-empty"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        is_empty = not commit.subject
        should_be_empty = config.condition == RuleCondition.ALWAYS

        if is_empty != should_be_empty:
            msg = (
                "subject may not be empty"
                if not should_be_empty
                else "subject must be empty"
            )
            return self._create_error(config, msg)
        return None


class SubjectCaseRule(BaseRule):
    """Enforce one or more case styles on the subject. Rule name: ``subject-case``."""

    @property
    def name(self) -> str:
        return "subject-case"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.subject or config.value is None:
            return None

        case_types = (
            config.value if isinstance(config.value, list) else [config.value]
        )

        matches_any = any(
            CaseValidator.validate(commit.subject, CaseType(case_type))
            for case_type in case_types
        )

        should_match = config.condition == RuleCondition.ALWAYS

        if matches_any != should_match:
            return self._create_error(
                config, f"subject must match case {config.value}"
            )
        return None


class SubjectFullStopRule(BaseRule):
    """Require or forbid a trailing punctuation character. Rule name: ``subject-full-stop``."""

    @property
    def name(self) -> str:
        return "subject-full-stop"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.subject:
            return None

        stop_char = config.value if config.value is not None else "."
        ends_with_stop = commit.subject.endswith(stop_char)
        should_end_with_stop = config.condition == RuleCondition.ALWAYS

        if ends_with_stop != should_end_with_stop:
            msg = (
                f"subject must end with '{stop_char}'"
                if should_end_with_stop
                else f"subject may not end with '{stop_char}'"
            )
            return self._create_error(config, msg)
        return None


class SubjectMinLengthRule(BaseRule):
    """Enforce a minimum subject length. Rule name: ``subject-min-length``."""

    @property
    def name(self) -> str:
        return "subject-min-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.subject:
            return None

        min_length = config.value if config.value is not None else 0
        is_valid = len(commit.subject) >= min_length
        should_be_valid = config.condition == RuleCondition.ALWAYS

        if is_valid != should_be_valid:
            return self._create_error(
                config, f"subject must be at least {min_length} characters"
            )
        return None


class SubjectMaxLengthRule(BaseRule):
    """Enforce a maximum subject length. Rule name: ``subject-max-length``."""

    @property
    def name(self) -> str:
        return "subject-max-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.subject:
            return None

        max_length = config.value if config.value is not None else float("inf")
        is_valid = len(commit.subject) <= max_length
        should_be_valid = config.condition == RuleCondition.ALWAYS

        if is_valid != should_be_valid:
            return self._create_error(
                config, f"subject must be at most {max_length} characters"
            )
        return None
