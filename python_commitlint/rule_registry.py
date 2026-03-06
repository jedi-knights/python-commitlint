from python_commitlint.protocols import RuleProtocol
from python_commitlint.rules import (
    BodyCaseRule,
    BodyEmptyRule,
    BodyFullStopRule,
    BodyLeadingBlankRule,
    BodyMaxLengthRule,
    BodyMaxLineLengthRule,
    BodyMinLengthRule,
    FooterEmptyRule,
    FooterLeadingBlankRule,
    FooterMaxLengthRule,
    FooterMaxLineLengthRule,
    FooterMinLengthRule,
    HeaderCaseRule,
    HeaderFullStopRule,
    HeaderMaxLengthRule,
    HeaderMinLengthRule,
    HeaderTrimRule,
    ScopeCaseRule,
    ScopeEmptyRule,
    ScopeEnumRule,
    ScopeMaxLengthRule,
    ScopeMinLengthRule,
    SubjectCaseRule,
    SubjectEmptyRule,
    SubjectFullStopRule,
    SubjectMaxLengthRule,
    SubjectMinLengthRule,
    TypeCaseRule,
    TypeEmptyRule,
    TypeEnumRule,
    TypeMaxLengthRule,
    TypeMinLengthRule,
)


class RuleRegistry:
    def __init__(self) -> None:
        self._rules: dict[str, RuleProtocol] = {}

    def register(self, rule: RuleProtocol) -> None:
        self._rules[rule.name] = rule

    def get(self, name: str) -> RuleProtocol | None:
        return self._rules.get(name)

    def get_all(self) -> dict[str, RuleProtocol]:
        return self._rules.copy()


class RuleRegistryFactory:
    @staticmethod
    def create() -> RuleRegistry:
        return RuleRegistry()

    @staticmethod
    def create_with_default_rules() -> RuleRegistry:
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
