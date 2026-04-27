import pytest

from python_commitlint.core.enums import RuleCondition, Severity
from python_commitlint.core.models import CommitMessage, RuleConfig
from python_commitlint.rules.subject_rules import (
    SubjectCaseRule,
    SubjectEmptyRule,
    SubjectFullStopRule,
    SubjectMaxLengthRule,
    SubjectMinLengthRule,
)


def _commit(subject: str = "add new feature") -> CommitMessage:
    return CommitMessage(
        raw=f"feat: {subject}",
        header=f"feat: {subject}",
        type="feat",
        subject=subject,
        is_conventional=True,
    )


def _config(
    condition: RuleCondition, value=None, severity: Severity = Severity.ERROR
) -> RuleConfig:
    return RuleConfig(severity=severity, condition=condition, value=value)


# --- SubjectEmptyRule ---


def test_subject_empty_rule_passes_when_non_empty_with_never() -> None:
    rule = SubjectEmptyRule()
    assert (
        rule.validate(_commit("add feature"), _config(RuleCondition.NEVER))
        is None
    )


def test_subject_empty_rule_fails_when_empty_with_never() -> None:
    rule = SubjectEmptyRule()
    commit = CommitMessage(raw="feat:", header="feat:", type="feat", subject="")
    result = rule.validate(commit, _config(RuleCondition.NEVER))
    assert result is not None
    assert "empty" in result.message


def test_subject_empty_rule_passes_when_empty_with_always() -> None:
    rule = SubjectEmptyRule()
    commit = CommitMessage(raw="feat:", header="feat:", type="feat", subject="")
    assert rule.validate(commit, _config(RuleCondition.ALWAYS)) is None


def test_subject_empty_rule_fails_when_non_empty_with_always() -> None:
    rule = SubjectEmptyRule()
    result = rule.validate(
        _commit("add feature"), _config(RuleCondition.ALWAYS)
    )
    assert result is not None


def test_subject_empty_rule_name() -> None:
    assert SubjectEmptyRule().name == "subject-empty"


# --- SubjectCaseRule ---


@pytest.mark.parametrize(
    "subject,cases,condition,should_fail",
    [
        (
            "add feature",
            ["sentence-case", "pascal-case"],
            RuleCondition.NEVER,
            False,
        ),
        ("Add feature", ["sentence-case"], RuleCondition.NEVER, True),
        ("add feature", ["lower-case"], RuleCondition.ALWAYS, False),
        ("Add Feature", ["lower-case"], RuleCondition.ALWAYS, True),
        ("ADD FEATURE", ["upper-case"], RuleCondition.ALWAYS, False),
    ],
)
def test_subject_case_rule(
    subject: str, cases: list, condition: RuleCondition, should_fail: bool
) -> None:
    rule = SubjectCaseRule()
    result = rule.validate(_commit(subject), _config(condition, value=cases))
    assert (result is not None) == should_fail


def test_subject_case_rule_single_case_string_value() -> None:
    rule = SubjectCaseRule()
    config = _config(RuleCondition.ALWAYS, value="lower-case")
    assert rule.validate(_commit("add feature"), config) is None


def test_subject_case_rule_skips_empty_subject() -> None:
    rule = SubjectCaseRule()
    commit = CommitMessage(raw="feat:", header="feat:", type="feat", subject="")
    assert (
        rule.validate(
            commit, _config(RuleCondition.ALWAYS, value=["lower-case"])
        )
        is None
    )


def test_subject_case_rule_name() -> None:
    assert SubjectCaseRule().name == "subject-case"


# --- SubjectFullStopRule ---


def test_subject_full_stop_rule_passes_without_period_with_never() -> None:
    rule = SubjectFullStopRule()
    assert (
        rule.validate(
            _commit("add feature"), _config(RuleCondition.NEVER, value=".")
        )
        is None
    )


def test_subject_full_stop_rule_fails_with_period_with_never() -> None:
    rule = SubjectFullStopRule()
    result = rule.validate(
        _commit("add feature."), _config(RuleCondition.NEVER, value=".")
    )
    assert result is not None
    assert "." in result.message


def test_subject_full_stop_rule_passes_with_period_with_always() -> None:
    rule = SubjectFullStopRule()
    assert (
        rule.validate(
            _commit("add feature."), _config(RuleCondition.ALWAYS, value=".")
        )
        is None
    )


def test_subject_full_stop_rule_fails_without_period_with_always() -> None:
    rule = SubjectFullStopRule()
    result = rule.validate(
        _commit("add feature"), _config(RuleCondition.ALWAYS, value=".")
    )
    assert result is not None


def test_subject_full_stop_rule_uses_default_period() -> None:
    rule = SubjectFullStopRule()
    result = rule.validate(
        _commit("add feature."), _config(RuleCondition.NEVER)
    )
    assert result is not None


def test_subject_full_stop_rule_skips_empty_subject() -> None:
    rule = SubjectFullStopRule()
    commit = CommitMessage(raw="feat:", header="feat:", type="feat", subject="")
    assert (
        rule.validate(commit, _config(RuleCondition.NEVER, value=".")) is None
    )


def test_subject_full_stop_rule_name() -> None:
    assert SubjectFullStopRule().name == "subject-full-stop"


# --- SubjectMinLengthRule ---


def test_subject_min_length_rule_passes_when_meets_min() -> None:
    rule = SubjectMinLengthRule()
    assert (
        rule.validate(
            _commit("add feature"), _config(RuleCondition.ALWAYS, value=3)
        )
        is None
    )


def test_subject_min_length_rule_fails_when_below_min() -> None:
    rule = SubjectMinLengthRule()
    result = rule.validate(
        _commit("hi"), _config(RuleCondition.ALWAYS, value=100)
    )
    assert result is not None
    assert "100" in result.message


def test_subject_min_length_rule_skips_empty_subject() -> None:
    rule = SubjectMinLengthRule()
    commit = CommitMessage(raw="feat:", header="feat:", type="feat", subject="")
    assert rule.validate(commit, _config(RuleCondition.ALWAYS, value=5)) is None


def test_subject_min_length_rule_name() -> None:
    assert SubjectMinLengthRule().name == "subject-min-length"


# --- SubjectMaxLengthRule ---


def test_subject_max_length_rule_passes_when_within_max() -> None:
    rule = SubjectMaxLengthRule()
    assert (
        rule.validate(
            _commit("add feature"), _config(RuleCondition.ALWAYS, value=100)
        )
        is None
    )


def test_subject_max_length_rule_fails_when_exceeds_max() -> None:
    rule = SubjectMaxLengthRule()
    result = rule.validate(
        _commit("add feature"), _config(RuleCondition.ALWAYS, value=5)
    )
    assert result is not None
    assert "5" in result.message


def test_subject_max_length_rule_skips_empty_subject() -> None:
    rule = SubjectMaxLengthRule()
    commit = CommitMessage(raw="feat:", header="feat:", type="feat", subject="")
    assert rule.validate(commit, _config(RuleCondition.ALWAYS, value=1)) is None


def test_subject_max_length_rule_name() -> None:
    assert SubjectMaxLengthRule().name == "subject-max-length"
