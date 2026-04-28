"""Enumerations shared across the linter, parser, rules, and configuration."""

from enum import StrEnum


class Severity(StrEnum):
    """How a rule violation is reported.

    ``DISABLED`` rules are skipped entirely. ``WARNING`` violations do not
    fail the lint; ``ERROR`` violations do.
    """

    DISABLED = "disabled"
    WARNING = "warning"
    ERROR = "error"


class RuleCondition(StrEnum):
    """The polarity of a rule's expectation.

    ``ALWAYS`` means the rule's check must hold; ``NEVER`` means it must
    not. For example, ``subject-full-stop`` with ``NEVER`` forbids a
    trailing period on the subject.
    """

    ALWAYS = "always"
    NEVER = "never"


class CaseType(StrEnum):
    """Recognized case styles for commit message components."""

    LOWER_CASE = "lower-case"
    UPPER_CASE = "upper-case"
    CAMEL_CASE = "camel-case"
    KEBAB_CASE = "kebab-case"
    PASCAL_CASE = "pascal-case"
    SENTENCE_CASE = "sentence-case"
    SNAKE_CASE = "snake-case"
    START_CASE = "start-case"
