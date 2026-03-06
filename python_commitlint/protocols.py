from typing import Protocol

from python_commitlint.models import (
    CommitMessage,
    Configuration,
    LintResult,
    RuleConfig,
    ValidationError,
)


class CommitParserProtocol(Protocol):
    def parse(self, message: str) -> CommitMessage: ...


class RuleProtocol(Protocol):
    @property
    def name(self) -> str: ...

    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None: ...


class ConfigurationLoaderProtocol(Protocol):
    def load(self, config_path: str | None = None) -> Configuration: ...


class CommitLinterProtocol(Protocol):
    def lint(self, message: str) -> LintResult: ...
