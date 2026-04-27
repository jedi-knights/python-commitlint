"""Registry that holds rules by name and a factory for the default rule set."""

from python_commitlint.core.protocols import RuleProtocol
from python_commitlint.rules.body_rules import (
    BodyCaseRule,
    BodyEmptyRule,
    BodyFullStopRule,
    BodyLeadingBlankRule,
    BodyMaxLengthRule,
    BodyMaxLineLengthRule,
    BodyMinLengthRule,
)
from python_commitlint.rules.footer_rules import (
    FooterEmptyRule,
    FooterLeadingBlankRule,
    FooterMaxLengthRule,
    FooterMaxLineLengthRule,
    FooterMinLengthRule,
)
from python_commitlint.rules.header_rules import (
    HeaderCaseRule,
    HeaderFullStopRule,
    HeaderMaxLengthRule,
    HeaderMinLengthRule,
    HeaderTrimRule,
)
from python_commitlint.rules.scope_rules import (
    ScopeCaseRule,
    ScopeEmptyRule,
    ScopeEnumRule,
    ScopeMaxLengthRule,
    ScopeMinLengthRule,
)
from python_commitlint.rules.subject_rules import (
    SubjectCaseRule,
    SubjectEmptyRule,
    SubjectFullStopRule,
    SubjectMaxLengthRule,
    SubjectMinLengthRule,
)
from python_commitlint.rules.type_rules import (
    TypeCaseRule,
    TypeEmptyRule,
    TypeEnumRule,
    TypeMaxLengthRule,
    TypeMinLengthRule,
)


class RuleRegistry:
    """Maps rule names to :class:`RuleProtocol` implementations.

    The linter consults the registry to resolve a configuration entry's
    rule name to the rule object that knows how to validate it. Unknown
    rule names are silently skipped by the linter, so registries can be
    populated with any subset of the built-ins or with user-defined rules.
    """

    def __init__(self) -> None:
        """Create an empty registry."""
        self._rules: dict[str, RuleProtocol] = {}

    def register(self, rule: RuleProtocol) -> None:
        """Register ``rule`` under its own ``name``.

        Args:
            rule: A rule instance whose ``name`` will be used as the key.
                Re-registering an existing name overwrites the prior entry.
        """
        self._rules[rule.name] = rule

    def get(self, name: str) -> RuleProtocol | None:
        """Return the rule registered under ``name`` or ``None``."""
        return self._rules.get(name)

    def get_all(self) -> dict[str, RuleProtocol]:
        """Return a shallow copy of the registry contents."""
        return self._rules.copy()


class RuleRegistryFactory:
    """Constructs :class:`RuleRegistry` instances."""

    @staticmethod
    def create() -> RuleRegistry:
        """Return an empty :class:`RuleRegistry`."""
        return RuleRegistry()

    @staticmethod
    def create_with_default_rules() -> RuleRegistry:
        """Return a registry populated with every built-in rule."""
        registry = RuleRegistry()

        rules: list[RuleProtocol] = [
            TypeEmptyRule(),
            TypeCaseRule(),
            TypeEnumRule(),
            TypeMinLengthRule(),
            TypeMaxLengthRule(),
            SubjectEmptyRule(),
            SubjectCaseRule(),
            SubjectFullStopRule(),
            SubjectMinLengthRule(),
            SubjectMaxLengthRule(),
            ScopeEmptyRule(),
            ScopeCaseRule(),
            ScopeEnumRule(),
            ScopeMinLengthRule(),
            ScopeMaxLengthRule(),
            HeaderMaxLengthRule(),
            HeaderMinLengthRule(),
            HeaderTrimRule(),
            HeaderFullStopRule(),
            HeaderCaseRule(),
            BodyEmptyRule(),
            BodyLeadingBlankRule(),
            BodyMaxLengthRule(),
            BodyMaxLineLengthRule(),
            BodyMinLengthRule(),
            BodyFullStopRule(),
            BodyCaseRule(),
            FooterEmptyRule(),
            FooterLeadingBlankRule(),
            FooterMaxLengthRule(),
            FooterMaxLineLengthRule(),
            FooterMinLengthRule(),
        ]

        for rule in rules:
            registry.register(rule)

        return registry
