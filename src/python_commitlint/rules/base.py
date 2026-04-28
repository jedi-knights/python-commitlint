"""Abstract base class for built-in commitlint rules."""

from abc import ABC, abstractmethod

from python_commitlint.core.models import (
    CommitMessage,
    RuleConfig,
    ValidationError,
)
from python_commitlint.core.protocols import RuleProtocol


def config_value_or[T](config: RuleConfig, default: T) -> T:
    """Return ``config.value`` if it is not ``None``, otherwise ``default``.

    Avoids the falsy-zero bug of ``config.value or default``: a configured
    ``value: 0`` is preserved, not silently replaced by the default.

    Note:
        ``RuleConfig.value`` is typed ``Any``, so the ``T`` return type is
        nominally a lie when the YAML stores a value whose Python type
        doesn't match ``default``. Callers are expected to validate the
        shape of ``config.value`` themselves (or accept downstream
        ``TypeError`` if the YAML is malformed).
    """
    return config.value if config.value is not None else default


class BaseRule(RuleProtocol, ABC):
    """Abstract base for all built-in commitlint rules.

    Inheriting from :class:`RuleProtocol` couples the ABC and the structural
    Protocol so they cannot drift independently — adding a method to
    ``RuleProtocol`` immediately makes ``BaseRule`` (and every subclass)
    fail to instantiate.

    Third-party rules need not inherit from ``BaseRule``. Any class that
    structurally implements :class:`RuleProtocol` (a ``name`` property
    and a ``validate`` method with the correct signature) can be passed
    to :meth:`RuleRegistry.register`.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The rule's stable identifier (e.g. ``type-case``)."""

    @abstractmethod
    def validate(
        self, commit: CommitMessage, config: RuleConfig
    ) -> ValidationError | None:
        """Apply the rule to ``commit`` under ``config``.

        Args:
            commit: Parsed commit to validate.
            config: This rule's severity, condition, and optional value.

        Returns:
            A :class:`ValidationError` if violated, otherwise ``None``.
        """

    def _create_error(
        self, config: RuleConfig, message: str
    ) -> ValidationError:
        """Construct a :class:`ValidationError` carrying this rule's name.

        Helper for subclasses so they don't repeat the boilerplate of
        threading ``self.name`` and ``config.severity`` through every
        violation site.
        """
        return ValidationError(
            rule=self.name,
            message=message,
            severity=config.severity,
        )
