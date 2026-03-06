from python_commitlint.case_validators import CaseValidator
from python_commitlint.enums import CaseType, RuleCondition
from python_commitlint.models import (
    CommitMessage,
    RuleConfig,
    ValidationError,
)
from python_commitlint.rules.base import BaseRule


class BodyEmptyRule(BaseRule):
    @property
    def name(self) -> str:
        return "body-empty"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        is_empty = not commit.body
        should_be_empty = config.condition == RuleCondition.ALWAYS

        if is_empty != should_be_empty:
            msg = (
                "body may not be empty"
                if not should_be_empty
                else "body must be empty"
            )
            return self._create_error(config, msg)
        return None


class BodyLeadingBlankRule(BaseRule):
    @property
    def name(self) -> str:
        return "body-leading-blank"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.body:
            return None

        lines = commit.raw.split("\n")
        if len(lines) < 2:
            return None

        has_blank = len(lines) > 1 and not lines[1].strip()
        should_have_blank = config.condition == RuleCondition.ALWAYS

        if has_blank != should_have_blank:
            msg = (
                "body must have leading blank line"
                if should_have_blank
                else "body must not have leading blank line"
            )
            return self._create_error(config, msg)
        return None


class BodyMaxLengthRule(BaseRule):
    @property
    def name(self) -> str:
        return "body-max-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.body:
            return None

        max_length = config.value or float("inf")
        is_valid = len(commit.body) <= max_length
        should_be_valid = config.condition == RuleCondition.ALWAYS

        if is_valid != should_be_valid:
            return self._create_error(
                config, f"body must be at most {max_length} characters"
            )
        return None


class BodyMaxLineLengthRule(BaseRule):
    @property
    def name(self) -> str:
        return "body-max-line-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.body:
            return None

        max_length = config.value or float("inf")
        lines = commit.body.split("\n")

        for line in lines:
            if "http://" in line or "https://" in line:
                continue
            if len(line) > max_length:
                should_be_valid = config.condition == RuleCondition.ALWAYS
                if should_be_valid:
                    return self._create_error(
                        config,
                        f"body lines must be at most {max_length} characters",
                    )
        return None


class BodyMinLengthRule(BaseRule):
    @property
    def name(self) -> str:
        return "body-min-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.body:
            return None

        min_length = config.value or 0
        is_valid = len(commit.body) >= min_length
        should_be_valid = config.condition == RuleCondition.ALWAYS

        if is_valid != should_be_valid:
            return self._create_error(
                config, f"body must be at least {min_length} characters"
            )
        return None


class BodyFullStopRule(BaseRule):
    @property
    def name(self) -> str:
        return "body-full-stop"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.body:
            return None

        stop_char = config.value or "."
        ends_with_stop = commit.body.rstrip().endswith(stop_char)
        should_end_with_stop = config.condition == RuleCondition.ALWAYS

        if ends_with_stop != should_end_with_stop:
            msg = (
                f"body must end with '{stop_char}'"
                if should_end_with_stop
                else f"body may not end with '{stop_char}'"
            )
            return self._create_error(config, msg)
        return None


class BodyCaseRule(BaseRule):
    @property
    def name(self) -> str:
        return "body-case"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.body:
            return None

        case_types = (
            config.value if isinstance(config.value, list) else [config.value]
        )

        matches_any = any(
            CaseValidator.validate(commit.body, CaseType(case_type))
            for case_type in case_types
        )

        should_match = config.condition == RuleCondition.ALWAYS

        if matches_any != should_match:
            return self._create_error(
                config, f"body must match case {config.value}"
            )
        return None
