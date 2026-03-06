import pytest

from python_commitlint.enums import RuleCondition, Severity
from python_commitlint.models import CommitMessage, RuleConfig
from python_commitlint.rules.scope_rules import (
    ScopeCaseRule,
    ScopeEmptyRule,
    ScopeEnumRule,
    ScopeMaxLengthRule,
    ScopeMinLengthRule,
)


def _commit(scope: str = "api") -> CommitMessage:
    return CommitMessage(
        raw=f"feat({scope}): subject",
        header=f"feat({scope}): subject",
        type="feat",
        scope=scope,
        subject="subject",
    )


def _commit_no_scope() -> CommitMessage:
    return CommitMessage(raw="feat: subject", header="feat: subject", type="feat", subject="subject")


def _config(condition: RuleCondition, value=None, severity: Severity = Severity.ERROR) -> RuleConfig:
    return RuleConfig(severity=severity, condition=condition, value=value)


# --- ScopeEmptyRule ---

def test_scope_empty_rule_passes_non_empty_with_never() -> None:
    rule = ScopeEmptyRule()
    assert rule.validate(_commit("api"), _config(RuleCondition.NEVER)) is None


def test_scope_empty_rule_fails_empty_with_never() -> None:
    rule = ScopeEmptyRule()
    result = rule.validate(_commit_no_scope(), _config(RuleCondition.NEVER))
    assert result is not None
    assert "empty" in result.message


def test_scope_empty_rule_passes_empty_with_always() -> None:
    rule = ScopeEmptyRule()
    assert rule.validate(_commit_no_scope(), _config(RuleCondition.ALWAYS)) is None


def test_scope_empty_rule_fails_non_empty_with_always() -> None:
    rule = ScopeEmptyRule()
    result = rule.validate(_commit("api"), _config(RuleCondition.ALWAYS))
    assert result is not None


def test_scope_empty_rule_name() -> None:
    assert ScopeEmptyRule().name == "scope-empty"


# --- ScopeCaseRule ---

@pytest.mark.parametrize("scope,case_value,condition,should_fail", [
    ("api", "lower-case", RuleCondition.ALWAYS, False),
    ("API", "lower-case", RuleCondition.ALWAYS, True),
    ("API", "upper-case", RuleCondition.ALWAYS, False),
    ("api", "upper-case", RuleCondition.ALWAYS, True),
    ("myApi", "camel-case", RuleCondition.ALWAYS, False),
    ("my-api", "kebab-case", RuleCondition.ALWAYS, False),
])
def test_scope_case_rule(scope: str, case_value: str, condition: RuleCondition, should_fail: bool) -> None:
    rule = ScopeCaseRule()
    result = rule.validate(_commit(scope), _config(condition, value=case_value))
    assert (result is not None) == should_fail


def test_scope_case_rule_with_list_value() -> None:
    rule = ScopeCaseRule()
    config = _config(RuleCondition.ALWAYS, value=["lower-case", "kebab-case"])
    assert rule.validate(_commit("my-scope"), config) is None


def test_scope_case_rule_with_slash_delimiter() -> None:
    rule = ScopeCaseRule()
    commit = _commit("api/auth")
    config = _config(RuleCondition.ALWAYS, value="lower-case")
    assert rule.validate(commit, config) is None


def test_scope_case_rule_skips_empty_scope() -> None:
    rule = ScopeCaseRule()
    assert rule.validate(_commit_no_scope(), _config(RuleCondition.ALWAYS, value="lower-case")) is None


def test_scope_case_rule_name() -> None:
    assert ScopeCaseRule().name == "scope-case"


# --- ScopeEnumRule ---

def test_scope_enum_rule_passes_when_scope_in_enum() -> None:
    rule = ScopeEnumRule()
    config = _config(RuleCondition.ALWAYS, value=["api", "ui", "db"])
    assert rule.validate(_commit("api"), config) is None


def test_scope_enum_rule_fails_when_scope_not_in_enum() -> None:
    rule = ScopeEnumRule()
    config = _config(RuleCondition.ALWAYS, value=["api", "ui"])
    result = rule.validate(_commit("cli"), config)
    assert result is not None
    assert "api" in result.message


def test_scope_enum_rule_never_condition_passes_when_not_in_enum() -> None:
    rule = ScopeEnumRule()
    config = _config(RuleCondition.NEVER, value=["api"])
    assert rule.validate(_commit("ui"), config) is None


def test_scope_enum_rule_never_condition_fails_when_in_enum() -> None:
    rule = ScopeEnumRule()
    config = _config(RuleCondition.NEVER, value=["api"])
    result = rule.validate(_commit("api"), config)
    assert result is not None


def test_scope_enum_rule_with_slash_delimiter() -> None:
    rule = ScopeEnumRule()
    config = _config(RuleCondition.ALWAYS, value=["api", "auth"])
    commit = _commit("api/auth")
    assert rule.validate(commit, config) is None


def test_scope_enum_rule_skips_empty_scope() -> None:
    rule = ScopeEnumRule()
    config = _config(RuleCondition.ALWAYS, value=["api"])
    assert rule.validate(_commit_no_scope(), config) is None


def test_scope_enum_rule_name() -> None:
    assert ScopeEnumRule().name == "scope-enum"


# --- ScopeMinLengthRule ---

def test_scope_min_length_rule_passes_when_meets_min() -> None:
    rule = ScopeMinLengthRule()
    assert rule.validate(_commit("api"), _config(RuleCondition.ALWAYS, value=2)) is None


def test_scope_min_length_rule_fails_when_below_min() -> None:
    rule = ScopeMinLengthRule()
    result = rule.validate(_commit("a"), _config(RuleCondition.ALWAYS, value=5))
    assert result is not None
    assert "5" in result.message


def test_scope_min_length_rule_skips_empty_scope() -> None:
    rule = ScopeMinLengthRule()
    assert rule.validate(_commit_no_scope(), _config(RuleCondition.ALWAYS, value=5)) is None


def test_scope_min_length_rule_name() -> None:
    assert ScopeMinLengthRule().name == "scope-min-length"


# --- ScopeMaxLengthRule ---

def test_scope_max_length_rule_passes_within_max() -> None:
    rule = ScopeMaxLengthRule()
    assert rule.validate(_commit("api"), _config(RuleCondition.ALWAYS, value=10)) is None


def test_scope_max_length_rule_fails_when_exceeds_max() -> None:
    rule = ScopeMaxLengthRule()
    result = rule.validate(_commit("very-long-scope"), _config(RuleCondition.ALWAYS, value=5))
    assert result is not None
    assert "5" in result.message


def test_scope_max_length_rule_skips_empty_scope() -> None:
    rule = ScopeMaxLengthRule()
    assert rule.validate(_commit_no_scope(), _config(RuleCondition.ALWAYS, value=1)) is None


def test_scope_max_length_rule_name() -> None:
    assert ScopeMaxLengthRule().name == "scope-max-length"
