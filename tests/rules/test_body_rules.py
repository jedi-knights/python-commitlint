import pytest

from python_commitlint.core.enums import RuleCondition
from python_commitlint.core.models import CommitMessage
from python_commitlint.rules.body_rules import (
    BodyCaseRule,
    BodyEmptyRule,
    BodyFullStopRule,
    BodyLeadingBlankRule,
    BodyMaxLengthRule,
    BodyMaxLineLengthRule,
    BodyMinLengthRule,
)
from tests.rules._helpers import _config


def _commit(body: str = "", raw: str = "") -> CommitMessage:
    raw = raw or f"feat: subject\n\n{body}" if body else "feat: subject"
    return CommitMessage(
        raw=raw,
        header="feat: subject",
        type="feat",
        subject="subject",
        body=body,
        is_conventional=True,
    )


# --- BodyEmptyRule ---


def test_body_empty_rule_passes_empty_with_always() -> None:
    rule = BodyEmptyRule()
    assert rule.validate(_commit(), _config(RuleCondition.ALWAYS)) is None


def test_body_empty_rule_fails_non_empty_with_always() -> None:
    rule = BodyEmptyRule()
    result = rule.validate(_commit("some body"), _config(RuleCondition.ALWAYS))
    assert result is not None
    assert "empty" in result.message


def test_body_empty_rule_passes_non_empty_with_never() -> None:
    rule = BodyEmptyRule()
    assert (
        rule.validate(_commit("some body"), _config(RuleCondition.NEVER))
        is None
    )


def test_body_empty_rule_fails_empty_with_never() -> None:
    rule = BodyEmptyRule()
    result = rule.validate(_commit(), _config(RuleCondition.NEVER))
    assert result is not None


def test_body_empty_rule_name() -> None:
    assert BodyEmptyRule().name == "body-empty"


# --- BodyLeadingBlankRule ---


def test_body_leading_blank_rule_passes_with_blank_line_and_always() -> None:
    rule = BodyLeadingBlankRule()
    raw = "feat: subject\n\nbody content"
    commit = CommitMessage(
        raw=raw,
        header="feat: subject",
        type="feat",
        subject="subject",
        body="body content",
    )
    assert rule.validate(commit, _config(RuleCondition.ALWAYS)) is None


def test_body_leading_blank_rule_fails_without_blank_line_and_always() -> None:
    rule = BodyLeadingBlankRule()
    raw = "feat: subject\nbody content"
    commit = CommitMessage(
        raw=raw,
        header="feat: subject",
        type="feat",
        subject="subject",
        body="body content",
    )
    result = rule.validate(commit, _config(RuleCondition.ALWAYS))
    assert result is not None
    assert "blank" in result.message


def test_body_leading_blank_rule_skips_empty_body() -> None:
    rule = BodyLeadingBlankRule()
    assert rule.validate(_commit(), _config(RuleCondition.ALWAYS)) is None


def test_body_leading_blank_rule_skips_single_line_commit() -> None:
    rule = BodyLeadingBlankRule()
    commit = CommitMessage(
        raw="feat: subject",
        header="feat: subject",
        type="feat",
        subject="subject",
        body="x",
    )
    assert rule.validate(commit, _config(RuleCondition.ALWAYS)) is None


def test_body_leading_blank_rule_name() -> None:
    assert BodyLeadingBlankRule().name == "body-leading-blank"


# --- BodyMaxLengthRule ---


def test_body_max_length_rule_passes_within_max() -> None:
    rule = BodyMaxLengthRule()
    assert (
        rule.validate(
            _commit("short body"), _config(RuleCondition.ALWAYS, value=100)
        )
        is None
    )


def test_body_max_length_rule_fails_when_exceeds_max() -> None:
    rule = BodyMaxLengthRule()
    result = rule.validate(
        _commit("a very long body text"), _config(RuleCondition.ALWAYS, value=5)
    )
    assert result is not None
    assert "5" in result.message


def test_body_max_length_rule_skips_empty_body() -> None:
    rule = BodyMaxLengthRule()
    assert (
        rule.validate(_commit(), _config(RuleCondition.ALWAYS, value=5)) is None
    )


def test_body_max_length_rule_name() -> None:
    assert BodyMaxLengthRule().name == "body-max-length"


# --- BodyMaxLineLengthRule ---


def test_body_max_line_length_rule_passes_within_limit() -> None:
    rule = BodyMaxLineLengthRule()
    assert (
        rule.validate(
            _commit("short line"), _config(RuleCondition.ALWAYS, value=100)
        )
        is None
    )


def test_body_max_line_length_rule_fails_on_long_line() -> None:
    rule = BodyMaxLineLengthRule()
    long_line = "x" * 120
    result = rule.validate(
        _commit(long_line), _config(RuleCondition.ALWAYS, value=100)
    )
    assert result is not None
    assert "100" in result.message


def test_body_max_line_length_rule_skips_url_only_lines() -> None:
    rule = BodyMaxLineLengthRule()
    url_line = "https://example.com/" + "x" * 200
    assert (
        rule.validate(
            _commit(url_line), _config(RuleCondition.ALWAYS, value=80)
        )
        is None
    )


def test_body_max_line_length_rule_does_not_skip_url_in_prose() -> None:
    rule = BodyMaxLineLengthRule()
    line = "See https://example.com/" + "x" * 200
    result = rule.validate(
        _commit(line), _config(RuleCondition.ALWAYS, value=80)
    )
    assert result is not None


def test_body_max_line_length_rule_skips_empty_body() -> None:
    rule = BodyMaxLineLengthRule()
    assert (
        rule.validate(_commit(), _config(RuleCondition.ALWAYS, value=10))
        is None
    )


def test_body_max_line_length_rule_name() -> None:
    assert BodyMaxLineLengthRule().name == "body-max-line-length"


# --- BodyMinLengthRule ---


def test_body_min_length_rule_passes_when_meets_min() -> None:
    rule = BodyMinLengthRule()
    assert (
        rule.validate(
            _commit("enough body"), _config(RuleCondition.ALWAYS, value=5)
        )
        is None
    )


def test_body_min_length_rule_fails_when_below_min() -> None:
    rule = BodyMinLengthRule()
    result = rule.validate(
        _commit("hi"), _config(RuleCondition.ALWAYS, value=50)
    )
    assert result is not None
    assert "50" in result.message


def test_body_min_length_rule_skips_empty_body() -> None:
    rule = BodyMinLengthRule()
    assert (
        rule.validate(_commit(), _config(RuleCondition.ALWAYS, value=5)) is None
    )


def test_body_min_length_rule_name() -> None:
    assert BodyMinLengthRule().name == "body-min-length"


# --- BodyFullStopRule ---


def test_body_full_stop_rule_passes_without_period_with_never() -> None:
    rule = BodyFullStopRule()
    assert (
        rule.validate(
            _commit("body text"), _config(RuleCondition.NEVER, value=".")
        )
        is None
    )


def test_body_full_stop_rule_fails_with_period_and_never() -> None:
    rule = BodyFullStopRule()
    result = rule.validate(
        _commit("body text."), _config(RuleCondition.NEVER, value=".")
    )
    assert result is not None
    assert "." in result.message


def test_body_full_stop_rule_passes_with_period_and_always() -> None:
    rule = BodyFullStopRule()
    assert (
        rule.validate(
            _commit("body text."), _config(RuleCondition.ALWAYS, value=".")
        )
        is None
    )


def test_body_full_stop_rule_skips_empty_body() -> None:
    rule = BodyFullStopRule()
    assert (
        rule.validate(_commit(), _config(RuleCondition.NEVER, value="."))
        is None
    )


def test_body_full_stop_rule_name() -> None:
    assert BodyFullStopRule().name == "body-full-stop"


# --- BodyCaseRule ---


@pytest.mark.parametrize(
    "body,cases,condition,should_fail",
    [
        ("lowercase body", ["lower-case"], RuleCondition.ALWAYS, False),
        ("Uppercase Body", ["lower-case"], RuleCondition.ALWAYS, True),
        ("Uppercase body text", ["sentence-case"], RuleCondition.ALWAYS, False),
    ],
)
def test_body_case_rule(
    body: str, cases: list, condition: RuleCondition, should_fail: bool
) -> None:
    rule = BodyCaseRule()
    result = rule.validate(_commit(body), _config(condition, value=cases))
    assert (result is not None) == should_fail


def test_body_case_rule_skips_empty_body() -> None:
    rule = BodyCaseRule()
    assert (
        rule.validate(
            _commit(), _config(RuleCondition.ALWAYS, value=["lower-case"])
        )
        is None
    )


def test_body_case_rule_name() -> None:
    assert BodyCaseRule().name == "body-case"
