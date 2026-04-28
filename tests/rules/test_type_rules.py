import pytest

from python_commitlint.core.enums import RuleCondition
from python_commitlint.core.models import CommitMessage
from python_commitlint.rules.type_rules import (
    TypeCaseRule,
    TypeEmptyRule,
    TypeEnumRule,
    TypeMaxLengthRule,
    TypeMinLengthRule,
)
from tests.rules._helpers import _config


def _commit(type: str = "feat") -> CommitMessage:
    return CommitMessage(
        raw=f"{type}: subject",
        header=f"{type}: subject",
        type=type,
        subject="subject",
        is_conventional=True,
    )


# --- TypeEmptyRule ---


@pytest.mark.parametrize(
    "type_val,condition,should_fail",
    [
        ("feat", RuleCondition.NEVER, False),
        ("", RuleCondition.NEVER, True),
        ("", RuleCondition.ALWAYS, False),
        ("feat", RuleCondition.ALWAYS, True),
    ],
)
def test_type_empty_rule(
    type_val: str, condition: RuleCondition, should_fail: bool
) -> None:
    rule = TypeEmptyRule()
    commit = CommitMessage(raw="", header="", type=type_val, subject="subject")
    result = rule.validate(commit, _config(condition))
    assert (result is not None) == should_fail


def test_type_empty_rule_error_message_not_empty() -> None:
    rule = TypeEmptyRule()
    commit = CommitMessage(raw="", header="", type="", subject="subject")
    result = rule.validate(commit, _config(RuleCondition.NEVER))
    assert result is not None
    assert "empty" in result.message


def test_type_empty_rule_error_message_must_be_empty() -> None:
    rule = TypeEmptyRule()
    commit = _commit("feat")
    result = rule.validate(commit, _config(RuleCondition.ALWAYS))
    assert result is not None
    assert "empty" in result.message


def test_type_empty_rule_name() -> None:
    assert TypeEmptyRule().name == "type-empty"


# --- TypeCaseRule ---


@pytest.mark.parametrize(
    "type_val,case,condition,should_fail",
    [
        ("feat", "lower-case", RuleCondition.ALWAYS, False),
        ("FEAT", "lower-case", RuleCondition.ALWAYS, True),
        ("FEAT", "upper-case", RuleCondition.ALWAYS, False),
        ("feat", "upper-case", RuleCondition.ALWAYS, True),
        ("feat", "lower-case", RuleCondition.NEVER, True),
    ],
)
def test_type_case_rule(
    type_val: str, case: str, condition: RuleCondition, should_fail: bool
) -> None:
    rule = TypeCaseRule()
    result = rule.validate(_commit(type_val), _config(condition, value=case))
    assert (result is not None) == should_fail


def test_type_case_rule_skips_empty_type() -> None:
    rule = TypeCaseRule()
    commit = CommitMessage(raw="", header="", type="", subject="subject")
    assert (
        rule.validate(commit, _config(RuleCondition.ALWAYS, value="lower-case"))
        is None
    )


def test_type_case_rule_name() -> None:
    assert TypeCaseRule().name == "type-case"


def test_type_case_rule_error_message() -> None:
    rule = TypeCaseRule()
    result = rule.validate(
        _commit("FEAT"), _config(RuleCondition.ALWAYS, value="lower-case")
    )
    assert result is not None
    assert "lower-case" in result.message


# --- TypeEnumRule ---


def test_type_enum_rule_valid_type_in_enum() -> None:
    rule = TypeEnumRule()
    config = _config(RuleCondition.ALWAYS, value=["feat", "fix"])
    assert rule.validate(_commit("feat"), config) is None


def test_type_enum_rule_invalid_type_not_in_enum() -> None:
    rule = TypeEnumRule()
    config = _config(RuleCondition.ALWAYS, value=["feat", "fix"])
    result = rule.validate(_commit("hotfix"), config)
    assert result is not None
    assert "feat" in result.message


def test_type_enum_rule_never_condition_passes_when_not_in_enum() -> None:
    rule = TypeEnumRule()
    config = _config(RuleCondition.NEVER, value=["feat"])
    assert rule.validate(_commit("fix"), config) is None


def test_type_enum_rule_never_condition_fails_when_in_enum() -> None:
    rule = TypeEnumRule()
    config = _config(RuleCondition.NEVER, value=["feat"])
    result = rule.validate(_commit("feat"), config)
    assert result is not None


def test_type_enum_rule_raises_when_value_missing() -> None:
    from python_commitlint.core.exceptions import ConfigurationError

    rule = TypeEnumRule()
    config = _config(RuleCondition.ALWAYS, value=None)
    with pytest.raises(ConfigurationError, match="requires a 'value'"):
        rule.validate(_commit("feat"), config)


def test_type_enum_rule_skips_empty_type() -> None:
    rule = TypeEnumRule()
    commit = CommitMessage(raw="", header="", type="", subject="subject")
    assert (
        rule.validate(commit, _config(RuleCondition.ALWAYS, value=["feat"]))
        is None
    )


def test_type_enum_rule_name() -> None:
    assert TypeEnumRule().name == "type-enum"


# --- TypeMinLengthRule ---


def test_type_min_length_rule_passes_when_meets_min() -> None:
    rule = TypeMinLengthRule()
    assert (
        rule.validate(_commit("feat"), _config(RuleCondition.ALWAYS, value=2))
        is None
    )


def test_type_min_length_rule_fails_when_below_min() -> None:
    rule = TypeMinLengthRule()
    result = rule.validate(
        _commit("feat"), _config(RuleCondition.ALWAYS, value=10)
    )
    assert result is not None
    assert "10" in result.message


def test_type_min_length_rule_skips_empty_type() -> None:
    rule = TypeMinLengthRule()
    commit = CommitMessage(raw="", header="", type="", subject="s")
    assert rule.validate(commit, _config(RuleCondition.ALWAYS, value=5)) is None


def test_type_min_length_rule_name() -> None:
    assert TypeMinLengthRule().name == "type-min-length"


# --- TypeMaxLengthRule ---


def test_type_max_length_rule_passes_when_within_max() -> None:
    rule = TypeMaxLengthRule()
    assert (
        rule.validate(_commit("feat"), _config(RuleCondition.ALWAYS, value=10))
        is None
    )


def test_type_max_length_rule_fails_when_exceeds_max() -> None:
    rule = TypeMaxLengthRule()
    result = rule.validate(
        _commit("feat"), _config(RuleCondition.ALWAYS, value=2)
    )
    assert result is not None
    assert "2" in result.message


def test_type_max_length_rule_skips_empty_type() -> None:
    rule = TypeMaxLengthRule()
    commit = CommitMessage(raw="", header="", type="", subject="s")
    assert rule.validate(commit, _config(RuleCondition.ALWAYS, value=1)) is None


def test_type_max_length_rule_name() -> None:
    assert TypeMaxLengthRule().name == "type-max-length"
