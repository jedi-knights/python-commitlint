"""Rules that validate the body — the paragraphs between header and footer."""

import re

from python_commitlint.core.enums import CaseType, RuleCondition
from python_commitlint.core.models import (
    CommitMessage,
    RuleConfig,
    ValidationError,
)
from python_commitlint.rules.base import BaseRule
from python_commitlint.rules.case_validators import CaseValidator

# A line that consists entirely of a URL (with optional surrounding whitespace)
# is exempt from body-max-line-length, matching upstream commitlint.
_URL_ONLY_LINE = re.compile(r"^\s*https?://\S+\s*$")


class BodyEmptyRule(BaseRule):
    """Require or forbid an empty body. Rule name: ``body-empty``."""

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
    """Require a blank line between header and body. Rule name: ``body-leading-blank``."""

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
    """Enforce a maximum total body length. Rule name: ``body-max-length``."""

    @property
    def name(self) -> str:
        return "body-max-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.body:
            return None

        max_length = config.value if config.value is not None else float("inf")
        is_valid = len(commit.body) <= max_length
        should_be_valid = config.condition == RuleCondition.ALWAYS

        if is_valid != should_be_valid:
            return self._create_error(
                config, f"body must be at most {max_length} characters"
            )
        return None


class BodyMaxLineLengthRule(BaseRule):
    """Enforce a per-line body length limit. Rule name: ``body-max-line-length``.

    Lines that consist entirely of a URL are exempt to match upstream commitlint.
    """

    @property
    def name(self) -> str:
        return "body-max-line-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.body:
            return None

        # Only the ALWAYS polarity is meaningful for a max-line-length
        # rule — "lines must NEVER be at most N characters" is nonsensical,
        # so under NEVER this rule is a no-op.
        if config.condition != RuleCondition.ALWAYS:
            return None

        max_length = config.value if config.value is not None else float("inf")
        for line in commit.body.split("\n"):
            if _URL_ONLY_LINE.match(line):
                continue
            if len(line) > max_length:
                return self._create_error(
                    config,
                    f"body lines must be at most {max_length} characters",
                )
        return None


class BodyMinLengthRule(BaseRule):
    """Enforce a minimum total body length. Rule name: ``body-min-length``."""

    @property
    def name(self) -> str:
        return "body-min-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.body:
            return None

        min_length = config.value if config.value is not None else 0
        is_valid = len(commit.body) >= min_length
        should_be_valid = config.condition == RuleCondition.ALWAYS

        if is_valid != should_be_valid:
            return self._create_error(
                config, f"body must be at least {min_length} characters"
            )
        return None


class BodyFullStopRule(BaseRule):
    """Require or forbid a trailing punctuation character. Rule name: ``body-full-stop``."""

    @property
    def name(self) -> str:
        return "body-full-stop"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.body:
            return None

        stop_char = config.value if config.value is not None else "."
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
    """Enforce a case style on the body text. Rule name: ``body-case``."""

    @property
    def name(self) -> str:
        return "body-case"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.body or config.value is None:
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
