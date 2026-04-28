"""Rules that validate the footer block (BREAKING CHANGE, ``token: value``)."""

import re

from python_commitlint.core.enums import RuleCondition
from python_commitlint.core.models import (
    CommitMessage,
    RuleConfig,
    ValidationError,
)
from python_commitlint.rules.base import BaseRule, config_value_or

_FOOTER_TOKEN_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^BREAKING[- ]CHANGE:"),
    re.compile(r"^[\w-]+:\s+"),
    re.compile(r"^[\w-]+\s+#\d+"),
)


def _is_footer_token_line(line: str) -> bool:
    return any(pattern.match(line) for pattern in _FOOTER_TOKEN_PATTERNS)


class FooterEmptyRule(BaseRule):
    """Require or forbid an empty footer. Rule name: ``footer-empty``."""

    @property
    def name(self) -> str:
        return "footer-empty"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        is_empty = not commit.footer
        should_be_empty = config.condition == RuleCondition.ALWAYS

        if is_empty != should_be_empty:
            msg = (
                "footer may not be empty"
                if not should_be_empty
                else "footer must be empty"
            )
            return self._create_error(config, msg)
        return None


class FooterLeadingBlankRule(BaseRule):
    """Require a blank line before the footer. Rule name: ``footer-leading-blank``."""

    @property
    def name(self) -> str:
        return "footer-leading-blank"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.footer:
            return None

        lines = commit.raw.split("\n")
        footer_start = self._find_footer_start(lines)

        if footer_start > 0:
            has_blank = not lines[footer_start - 1].strip()
            should_have_blank = config.condition == RuleCondition.ALWAYS

            if has_blank != should_have_blank:
                msg = (
                    "footer must have leading blank line"
                    if should_have_blank
                    else "footer must not have leading blank line"
                )
                return self._create_error(config, msg)
        return None

    def _find_footer_start(self, lines: list[str]) -> int:
        # Skip line 0 (the header) — its `type: subject` shape would
        # otherwise be mistaken for a footer token.
        for i in range(1, len(lines)):
            line = lines[i]
            if line and _is_footer_token_line(line):
                return i
        return -1


class FooterMaxLengthRule(BaseRule):
    """Enforce a maximum total footer length. Rule name: ``footer-max-length``."""

    @property
    def name(self) -> str:
        return "footer-max-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.footer:
            return None

        max_length = config_value_or(config, float("inf"))
        is_valid = len(commit.footer) <= max_length
        should_be_valid = config.condition == RuleCondition.ALWAYS

        if is_valid != should_be_valid:
            return self._create_error(
                config, f"footer must be at most {max_length} characters"
            )
        return None


class FooterMaxLineLengthRule(BaseRule):
    """Enforce a per-line footer length limit. Rule name: ``footer-max-line-length``."""

    @property
    def name(self) -> str:
        return "footer-max-line-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.footer:
            return None

        # Only the ALWAYS polarity is meaningful for a max-line-length
        # rule — "lines must NEVER be at most N characters" is nonsensical,
        # so under NEVER this rule is a no-op.
        if config.condition != RuleCondition.ALWAYS:
            return None

        max_length = config_value_or(config, float("inf"))
        for line in commit.footer.split("\n"):
            if len(line) > max_length:
                return self._create_error(
                    config,
                    f"footer lines must be at most {max_length} characters",
                )
        return None


class FooterMinLengthRule(BaseRule):
    """Enforce a minimum total footer length. Rule name: ``footer-min-length``."""

    @property
    def name(self) -> str:
        return "footer-min-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.footer:
            return None

        min_length = config_value_or(config, 0)
        is_valid = len(commit.footer) >= min_length
        should_be_valid = config.condition == RuleCondition.ALWAYS

        if is_valid != should_be_valid:
            return self._create_error(
                config, f"footer must be at least {min_length} characters"
            )
        return None
