from enum import StrEnum


class Severity(StrEnum):
    DISABLED = "disabled"
    WARNING = "warning"
    ERROR = "error"


class RuleCondition(StrEnum):
    ALWAYS = "always"
    NEVER = "never"


class CaseType(StrEnum):
    LOWER_CASE = "lower-case"
    UPPER_CASE = "upper-case"
    CAMEL_CASE = "camel-case"
    KEBAB_CASE = "kebab-case"
    PASCAL_CASE = "pascal-case"
    SENTENCE_CASE = "sentence-case"
    SNAKE_CASE = "snake-case"
    START_CASE = "start-case"


class CommitType(StrEnum):
    BUILD = "build"
    CHORE = "chore"
    CI = "ci"
    DOCS = "docs"
    FEAT = "feat"
    FIX = "fix"
    PERF = "perf"
    REFACTOR = "refactor"
    REVERT = "revert"
    STYLE = "style"
    TEST = "test"
