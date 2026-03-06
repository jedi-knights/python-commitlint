from abc import ABC, abstractmethod

from python_commitlint.models import (
    CommitMessage,
    RuleConfig,
    ValidationError,
)


class BaseRule(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        pass

    def _create_error(
        self, config: RuleConfig, message: str
    ) -> ValidationError:
        return ValidationError(
            rule=self.name,
            message=message,
            severity=config.severity,
        )
