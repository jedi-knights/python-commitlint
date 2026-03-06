import pytest

from python_commitlint.enums import RuleCondition, Severity
from python_commitlint.models import CommitMessage, RuleConfig
from python_commitlint.rules.header_rules import (
    HeaderCaseRule,
    HeaderFullStopRule,
    HeaderMaxLengthRule,
    HeaderMinLengthRule,
    HeaderTrimRule,
)


def _commit(header: str) -> CommitMessage:
    return CommitMessage(raw=header, header=header)


def _config(condition: RuleCondition, value=None, severity: Severity = Severity.ERROR) -> RuleConfig:
    return RuleConfig(severity=severity, condition=condition, value=value)


# --- HeaderMaxLengthRule ---

def test_header_max_length_rule_passes_within_max() -> None:
    rule = HeaderMaxLengthRule()
    assert rule.validate(_commit("feat: short header"), _config(RuleCondition.ALWAYS, value=100)) is None


def test_header_max_length_rule_fails_when_exceeds_max() -> None:
    rule = HeaderMaxLengthRule()
    result = rule.validate(_commit("feat: this is a very long header"), _config(RuleCondition.ALWAYS, value=10))
    assert result is not None
    assert "10" in result.message


def test_header_max_length_rule_passes_at_exact_boundary() -> None:
    rule = HeaderMaxLengthRule()
    header = "feat: ok"
    assert rule.validate(_commit(header), _config(RuleCondition.ALWAYS, value=len(header))) is None


def test_header_max_length_rule_never_condition_fails_when_within() -> None:
    rule = HeaderMaxLengthRule()
    result = rule.validate(_commit("feat: hi"), _config(RuleCondition.NEVER, value=100))
    assert result is not None


def test_header_max_length_rule_name() -> None:
    assert HeaderMaxLengthRule().name == "header-max-length"


# --- HeaderMinLengthRule ---

def test_header_min_length_rule_passes_when_meets_min() -> None:
    rule = HeaderMinLengthRule()
    assert rule.validate(_commit("feat: header"), _config(RuleCondition.ALWAYS, value=5)) is None


def test_header_min_length_rule_fails_when_below_min() -> None:
    rule = HeaderMinLengthRule()
    result = rule.validate(_commit("hi"), _config(RuleCondition.ALWAYS, value=50))
    assert result is not None
    assert "50" in result.message


def test_header_min_length_rule_name() -> None:
    assert HeaderMinLengthRule().name == "header-min-length"


# --- HeaderTrimRule ---

def test_header_trim_rule_passes_on_trimmed_header() -> None:
    rule = HeaderTrimRule()
    assert rule.validate(_commit("feat: header"), _config(RuleCondition.ALWAYS)) is None


def test_header_trim_rule_fails_on_leading_space() -> None:
    rule = HeaderTrimRule()
    result = rule.validate(_commit(" feat: header"), _config(RuleCondition.ALWAYS))
    assert result is not None
    assert "whitespace" in result.message


def test_header_trim_rule_fails_on_trailing_space() -> None:
    rule = HeaderTrimRule()
    result = rule.validate(_commit("feat: header "), _config(RuleCondition.ALWAYS))
    assert result is not None


def test_header_trim_rule_never_condition_fails_on_trimmed() -> None:
    rule = HeaderTrimRule()
    result = rule.validate(_commit("feat: header"), _config(RuleCondition.NEVER))
    assert result is not None


def test_header_trim_rule_name() -> None:
    assert HeaderTrimRule().name == "header-trim"


# --- HeaderFullStopRule ---

def test_header_full_stop_rule_passes_without_period_with_never() -> None:
    rule = HeaderFullStopRule()
    assert rule.validate(_commit("feat: header"), _config(RuleCondition.NEVER, value=".")) is None


def test_header_full_stop_rule_fails_with_period_and_never() -> None:
    rule = HeaderFullStopRule()
    result = rule.validate(_commit("feat: header."), _config(RuleCondition.NEVER, value="."))
    assert result is not None
    assert "." in result.message


def test_header_full_stop_rule_passes_with_period_and_always() -> None:
    rule = HeaderFullStopRule()
    assert rule.validate(_commit("feat: header."), _config(RuleCondition.ALWAYS, value=".")) is None


def test_header_full_stop_rule_skips_empty_header() -> None:
    rule = HeaderFullStopRule()
    assert rule.validate(_commit(""), _config(RuleCondition.NEVER, value=".")) is None


def test_header_full_stop_rule_name() -> None:
    assert HeaderFullStopRule().name == "header-full-stop"


# --- HeaderCaseRule ---

@pytest.mark.parametrize("header,cases,condition,should_fail", [
    ("feat: header", ["lower-case"], RuleCondition.ALWAYS, False),
    ("Feat: Header", ["lower-case"], RuleCondition.ALWAYS, True),
    ("FEAT: HEADER", ["upper-case"], RuleCondition.ALWAYS, False),
    ("feat: header", ["upper-case"], RuleCondition.ALWAYS, True),
])
def test_header_case_rule(header: str, cases: list, condition: RuleCondition, should_fail: bool) -> None:
    rule = HeaderCaseRule()
    result = rule.validate(_commit(header), _config(condition, value=cases))
    assert (result is not None) == should_fail


def test_header_case_rule_single_case_string_value() -> None:
    rule = HeaderCaseRule()
    config = _config(RuleCondition.ALWAYS, value="lower-case")
    assert rule.validate(_commit("feat: header"), config) is None


def test_header_case_rule_skips_empty_header() -> None:
    rule = HeaderCaseRule()
    assert rule.validate(_commit(""), _config(RuleCondition.ALWAYS, value=["lower-case"])) is None


def test_header_case_rule_name() -> None:
    assert HeaderCaseRule().name == "header-case"
