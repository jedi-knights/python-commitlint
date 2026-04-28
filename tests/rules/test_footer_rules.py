from python_commitlint.core.enums import RuleCondition
from python_commitlint.core.models import CommitMessage
from python_commitlint.rules.footer_rules import (
    FooterEmptyRule,
    FooterLeadingBlankRule,
    FooterMaxLengthRule,
    FooterMaxLineLengthRule,
    FooterMinLengthRule,
)
from tests.rules._helpers import _config


def _commit(footer: str = "", raw: str = "") -> CommitMessage:
    if not raw and footer:
        raw = f"feat: subject\n\nsome body\n\n{footer}"
    elif not raw:
        raw = "feat: subject"
    return CommitMessage(
        raw=raw,
        header="feat: subject",
        type="feat",
        subject="subject",
        footer=footer,
        is_conventional=True,
    )


# --- FooterEmptyRule ---


def test_footer_empty_rule_passes_empty_with_always() -> None:
    rule = FooterEmptyRule()
    assert rule.validate(_commit(), _config(RuleCondition.ALWAYS)) is None


def test_footer_empty_rule_fails_non_empty_with_always() -> None:
    rule = FooterEmptyRule()
    result = rule.validate(
        _commit("Reviewed-by: Bob"), _config(RuleCondition.ALWAYS)
    )
    assert result is not None
    assert "empty" in result.message


def test_footer_empty_rule_passes_non_empty_with_never() -> None:
    rule = FooterEmptyRule()
    assert (
        rule.validate(_commit("Reviewed-by: Bob"), _config(RuleCondition.NEVER))
        is None
    )


def test_footer_empty_rule_fails_empty_with_never() -> None:
    rule = FooterEmptyRule()
    result = rule.validate(_commit(), _config(RuleCondition.NEVER))
    assert result is not None


def test_footer_empty_rule_name() -> None:
    assert FooterEmptyRule().name == "footer-empty"


# --- FooterLeadingBlankRule ---


def test_footer_leading_blank_rule_passes_with_blank_line() -> None:
    rule = FooterLeadingBlankRule()
    raw = "feat: subject\n\nbody\n\nBREAKING CHANGE: something"
    commit = CommitMessage(
        raw=raw,
        header="feat: subject",
        type="feat",
        subject="subject",
        footer="BREAKING CHANGE: something",
    )
    assert rule.validate(commit, _config(RuleCondition.ALWAYS)) is None


def test_footer_leading_blank_rule_fails_without_blank_line() -> None:
    rule = FooterLeadingBlankRule()
    raw = "feat: subject\nbody\nBREAKING CHANGE: something"
    commit = CommitMessage(
        raw=raw,
        header="feat: subject",
        type="feat",
        subject="subject",
        footer="BREAKING CHANGE: something",
    )
    result = rule.validate(commit, _config(RuleCondition.ALWAYS))
    assert result is not None
    assert "blank" in result.message


def test_footer_leading_blank_rule_skips_empty_footer() -> None:
    rule = FooterLeadingBlankRule()
    assert rule.validate(_commit(), _config(RuleCondition.ALWAYS)) is None


def test_footer_leading_blank_rule_name() -> None:
    assert FooterLeadingBlankRule().name == "footer-leading-blank"


# --- FooterMaxLengthRule ---


def test_footer_max_length_rule_passes_within_max() -> None:
    rule = FooterMaxLengthRule()
    assert (
        rule.validate(
            _commit("Reviewed-by: Bob"),
            _config(RuleCondition.ALWAYS, value=100),
        )
        is None
    )


def test_footer_max_length_rule_fails_when_exceeds_max() -> None:
    rule = FooterMaxLengthRule()
    result = rule.validate(
        _commit("Reviewed-by: Bob"), _config(RuleCondition.ALWAYS, value=5)
    )
    assert result is not None
    assert "5" in result.message


def test_footer_max_length_rule_skips_empty_footer() -> None:
    rule = FooterMaxLengthRule()
    assert (
        rule.validate(_commit(), _config(RuleCondition.ALWAYS, value=5)) is None
    )


def test_footer_max_length_rule_name() -> None:
    assert FooterMaxLengthRule().name == "footer-max-length"


# --- FooterMaxLineLengthRule ---


def test_footer_max_line_length_rule_passes_within_limit() -> None:
    rule = FooterMaxLineLengthRule()
    assert (
        rule.validate(
            _commit("Reviewed-by: Bob"),
            _config(RuleCondition.ALWAYS, value=100),
        )
        is None
    )


def test_footer_max_line_length_rule_fails_on_long_line() -> None:
    rule = FooterMaxLineLengthRule()
    long_footer = "Reviewed-by: " + "x" * 200
    result = rule.validate(
        _commit(long_footer), _config(RuleCondition.ALWAYS, value=50)
    )
    assert result is not None
    assert "50" in result.message


def test_footer_max_line_length_rule_skips_empty_footer() -> None:
    rule = FooterMaxLineLengthRule()
    assert (
        rule.validate(_commit(), _config(RuleCondition.ALWAYS, value=10))
        is None
    )


def test_footer_max_line_length_rule_name() -> None:
    assert FooterMaxLineLengthRule().name == "footer-max-line-length"


# --- FooterMinLengthRule ---


def test_footer_min_length_rule_passes_when_meets_min() -> None:
    rule = FooterMinLengthRule()
    assert (
        rule.validate(
            _commit("Reviewed-by: Bob"), _config(RuleCondition.ALWAYS, value=5)
        )
        is None
    )


def test_footer_min_length_rule_fails_when_below_min() -> None:
    rule = FooterMinLengthRule()
    result = rule.validate(
        _commit("Bob"), _config(RuleCondition.ALWAYS, value=50)
    )
    assert result is not None
    assert "50" in result.message


def test_footer_min_length_rule_skips_empty_footer() -> None:
    rule = FooterMinLengthRule()
    assert (
        rule.validate(_commit(), _config(RuleCondition.ALWAYS, value=5)) is None
    )


def test_footer_min_length_rule_name() -> None:
    assert FooterMinLengthRule().name == "footer-min-length"
