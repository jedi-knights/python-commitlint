"""Shared helpers for rule unit tests.

Each rule test file constructs many ``RuleConfig`` instances; centralising
the factory here removes the per-file duplication.
"""

from typing import Any

from python_commitlint.core.enums import RuleCondition, Severity
from python_commitlint.core.models import RuleConfig


def _config(
    condition: RuleCondition,
    value: Any = None,
    severity: Severity = Severity.ERROR,
) -> RuleConfig:
    """Build a ``RuleConfig`` for tests.

    Args:
        condition: Whether the rule's check must always or never hold.
        value: Rule-specific argument; defaults to ``None``.
        severity: Severity for the rule. Defaults to ``ERROR`` so test
            assertions can match on ``result.errors`` directly.

    Returns:
        A populated :class:`RuleConfig`.
    """
    return RuleConfig(severity=severity, condition=condition, value=value)
