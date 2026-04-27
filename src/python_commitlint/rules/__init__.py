"""Built-in commitlint rules — type, scope, subject, header, body, footer.

Each rule implements :class:`~python_commitlint.core.protocols.RuleProtocol`
and is registered with a :class:`~python_commitlint.rules.registry.RuleRegistry`
so the linter can dispatch by rule name.
"""

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

__all__ = [
    "BodyCaseRule",
    "BodyEmptyRule",
    "BodyFullStopRule",
    "BodyLeadingBlankRule",
    "BodyMaxLengthRule",
    "BodyMaxLineLengthRule",
    "BodyMinLengthRule",
    "FooterEmptyRule",
    "FooterLeadingBlankRule",
    "FooterMaxLengthRule",
    "FooterMaxLineLengthRule",
    "FooterMinLengthRule",
    "HeaderCaseRule",
    "HeaderFullStopRule",
    "HeaderMaxLengthRule",
    "HeaderMinLengthRule",
    "HeaderTrimRule",
    "ScopeCaseRule",
    "ScopeEmptyRule",
    "ScopeEnumRule",
    "ScopeMaxLengthRule",
    "ScopeMinLengthRule",
    "SubjectCaseRule",
    "SubjectEmptyRule",
    "SubjectFullStopRule",
    "SubjectMaxLengthRule",
    "SubjectMinLengthRule",
    "TypeCaseRule",
    "TypeEmptyRule",
    "TypeEnumRule",
    "TypeMaxLengthRule",
    "TypeMinLengthRule",
]
