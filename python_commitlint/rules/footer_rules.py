from python_commitlint.enums import RuleCondition
from python_commitlint.models import (
    CommitMessage,
    RuleConfig,
    ValidationError,
)
from python_commitlint.rules.base import BaseRule


class FooterEmptyRule(BaseRule):
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
        for i, line in enumerate(lines):
            if line and any(
                line.startswith(prefix)
                for prefix in ["BREAKING CHANGE:", "BREAKING-CHANGE:"]
            ):
                return i
        return -1


class FooterMaxLengthRule(BaseRule):
    @property
    def name(self) -> str:
        return "footer-max-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.footer:
            return None

        max_length = config.value or float("inf")
        is_valid = len(commit.footer) <= max_length
        should_be_valid = config.condition == RuleCondition.ALWAYS

        if is_valid != should_be_valid:
            return self._create_error(
                config, f"footer must be at most {max_length} characters"
            )
        return None


class FooterMaxLineLengthRule(BaseRule):
    @property
    def name(self) -> str:
        return "footer-max-line-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.footer:
            return None

        max_length = config.value or float("inf")
        lines = commit.footer.split("\n")

        for line in lines:
            if len(line) > max_length:
                should_be_valid = config.condition == RuleCondition.ALWAYS
                if should_be_valid:
                    return self._create_error(
                        config,
                        f"footer lines must be at most {max_length} characters",
                    )
        return None


class FooterMinLengthRule(BaseRule):
    @property
    def name(self) -> str:
        return "footer-min-length"

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        if not commit.footer:
            return None

        min_length = config.value or 0
        is_valid = len(commit.footer) >= min_length
        should_be_valid = config.condition == RuleCondition.ALWAYS

        if is_valid != should_be_valid:
            return self._create_error(
                config, f"footer must be at least {min_length} characters"
            )
        return None
