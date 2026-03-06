from pathlib import Path

import pytest

from python_commitlint.enums import RuleCondition, Severity
from python_commitlint.linter import CommitLinter, CommitLinterFactory, _categorize_violation
from python_commitlint.models import ValidationError


# --- valid commits ---

@pytest.mark.parametrize("message", [
    "feat: add new feature",
    "fix(api): resolve timeout issue",
    "docs: update installation guide",
    "chore(deps): upgrade dependencies",
    "refactor: simplify error handling",
    "test: add integration tests",
    "style: format code",
    "perf: improve query speed",
    "ci: update pipeline config",
    "build: update build system",
    "revert: revert previous commit",
])
def test_valid_conventional_commits(linter: CommitLinter, message: str) -> None:
    result = linter.lint(message)
    assert result.valid is True
    assert result.has_errors is False


# --- invalid commits ---

@pytest.mark.parametrize("message", [
    "Feature: bad type format",
    "FEAT: uppercase type",
    "feat: subject ending in period.",
    "just a random message",
])
def test_invalid_conventional_commits(linter: CommitLinter, message: str) -> None:
    result = linter.lint(message)
    assert result.valid is False
    assert result.has_errors is True


# --- merge commits ---

def test_merge_commit_is_valid(linter: CommitLinter) -> None:
    result = linter.lint("Merge branch 'main' into feature/my-branch")
    assert result.valid is True
    assert result.has_errors is False


def test_merge_commit_with_merge_prefix_is_valid(linter: CommitLinter) -> None:
    result = linter.lint("Merge pull request #123 from feature/something")
    assert result.valid is True


# --- error details ---

def test_lint_result_has_type_case_error_for_uppercase_type(linter: CommitLinter) -> None:
    result = linter.lint("FEAT: uppercase type")
    assert result.has_errors is True
    assert any(e.rule == "type-case" for e in result.errors)


def test_lint_result_has_type_enum_error_for_unknown_type(linter: CommitLinter) -> None:
    result = linter.lint("FEAT: bad commit")
    assert any(e.rule == "type-enum" for e in result.errors)


def test_lint_error_has_severity_field(linter: CommitLinter) -> None:
    result = linter.lint("FEAT: bad commit")
    assert all(e.severity == Severity.ERROR for e in result.errors)


# --- warnings ---

def test_well_formed_commit_with_body_produces_no_warnings(linter: CommitLinter) -> None:
    result = linter.lint("feat: add feature\n\nbody content")
    assert result.valid is True
    assert result.has_warnings is False


# --- LintResult properties ---

def test_lint_result_has_errors_is_false_when_no_errors(linter: CommitLinter) -> None:
    result = linter.lint("feat: clean commit")
    assert result.has_errors is False


def test_lint_result_valid_is_false_when_has_errors(linter: CommitLinter) -> None:
    result = linter.lint("FEAT: bad")
    assert result.valid is False


# --- disabled rules are skipped ---

def test_disabled_rule_is_skipped(tmp_path: Path) -> None:
    config = tmp_path / ".commitlintrc.yaml"
    config.write_text("""
rules:
  type-enum:
    severity: disabled
    condition: always
    value:
      - feat
""")
    linter = CommitLinterFactory.create(config_path=str(config))
    result = linter.lint("chore: should pass since type-enum is disabled")
    assert result.valid is True


# --- unknown rule is ignored ---

def test_unknown_rule_in_config_is_ignored(tmp_path: Path) -> None:
    config = tmp_path / ".commitlintrc.yaml"
    config.write_text("""
rules:
  unknown-rule-xyz:
    severity: error
    condition: always
""")
    linter = CommitLinterFactory.create(config_path=str(config))
    result = linter.lint("feat: valid commit")
    assert result.valid is True


# --- factory ---

def test_factory_creates_linter() -> None:
    assert CommitLinterFactory.create() is not None


def test_factory_with_custom_config_path_accepts_valid_type(tmp_path: Path) -> None:
    config = tmp_path / ".commitlintrc.yaml"
    config.write_text("""
rules:
  type-enum:
    severity: error
    condition: always
    value:
      - feat
      - fix
""")
    linter = CommitLinterFactory.create(config_path=str(config))
    assert linter.lint("feat: valid type").valid is True


def test_factory_with_custom_config_rejects_unlisted_type(tmp_path: Path) -> None:
    config = tmp_path / ".commitlintrc.yaml"
    config.write_text("""
rules:
  type-enum:
    severity: error
    condition: always
    value:
      - feat
      - fix
""")
    linter = CommitLinterFactory.create(config_path=str(config))
    assert linter.lint("chore: not in enum").valid is False


# --- _categorize_violation helper ---

def test_categorize_violation_routes_error() -> None:
    errors: list[ValidationError] = []
    warnings: list[ValidationError] = []
    v = ValidationError(rule="r", message="m", severity=Severity.ERROR)
    _categorize_violation(v, errors, warnings)
    assert len(errors) == 1
    assert len(warnings) == 0


def test_categorize_violation_routes_warning() -> None:
    errors: list[ValidationError] = []
    warnings: list[ValidationError] = []
    v = ValidationError(rule="r", message="m", severity=Severity.WARNING)
    _categorize_violation(v, errors, warnings)
    assert len(errors) == 0
    assert len(warnings) == 1


def test_categorize_violation_ignores_disabled() -> None:
    errors: list[ValidationError] = []
    warnings: list[ValidationError] = []
    v = ValidationError(rule="r", message="m", severity=Severity.DISABLED)
    _categorize_violation(v, errors, warnings)
    assert len(errors) == 0
    assert len(warnings) == 0
