from enum import Enum


class Severity(str, Enum):
    DISABLED = "disabled"
    WARNING = "warning"
    ERROR = "error"


class RuleCondition(str, Enum):
    ALWAYS = "always"
    NEVER = "never"


class CaseType(str, Enum):
    LOWER_CASE = "lower-case"
    UPPER_CASE = "upper-case"
    CAMEL_CASE = "camel-case"
    KEBAB_CASE = "kebab-case"
    PASCAL_CASE = "pascal-case"
    SENTENCE_CASE = "sentence-case"
    SNAKE_CASE = "snake-case"
    START_CASE = "start-case"


class CommitType(str, Enum):
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
