from pathlib import Path

import pytest
from click.testing import CliRunner

from python_commitlint.cli import commitlint


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


# --- lint command: valid messages ---

def test_lint_valid_commit_exits_zero(runner: CliRunner) -> None:
    result = runner.invoke(commitlint, ["lint", "feat: add new feature"])
    assert result.exit_code == 0


def test_lint_valid_commit_prints_success(runner: CliRunner) -> None:
    result = runner.invoke(commitlint, ["lint", "feat: add new feature"])
    assert "valid" in result.output.lower()


def test_lint_valid_commit_with_scope_exits_zero(runner: CliRunner) -> None:
    result = runner.invoke(commitlint, ["lint", "fix(api): resolve timeout"])
    assert result.exit_code == 0


# --- lint command: invalid messages ---

def test_lint_invalid_type_case_exits_nonzero(runner: CliRunner) -> None:
    result = runner.invoke(commitlint, ["lint", "FEAT: bad commit"])
    assert result.exit_code == 1


def test_lint_invalid_type_case_prints_error(runner: CliRunner) -> None:
    result = runner.invoke(commitlint, ["lint", "FEAT: bad commit"])
    assert "type-case" in result.output


def test_lint_invalid_type_enum_prints_error(runner: CliRunner) -> None:
    result = runner.invoke(commitlint, ["lint", "FEAT: bad commit"])
    assert "type-enum" in result.output


def test_lint_subject_with_period_exits_nonzero(runner: CliRunner) -> None:
    result = runner.invoke(commitlint, ["lint", "feat: subject ending in period."])
    assert result.exit_code == 1


def test_lint_no_message_exits_nonzero(runner: CliRunner) -> None:
    result = runner.invoke(commitlint, ["lint"])
    assert result.exit_code == 1


def test_lint_no_message_prints_error(runner: CliRunner) -> None:
    result = runner.invoke(commitlint, ["lint"])
    assert "Error" in result.output or "error" in result.output.lower()


# --- lint command: merge commits ---

def test_lint_merge_commit_exits_zero(runner: CliRunner) -> None:
    result = runner.invoke(commitlint, ["lint", "Merge branch 'main' into feature"])
    assert result.exit_code == 0


# --- lint command: --format json ---

def test_lint_json_format_valid_commit(runner: CliRunner) -> None:
    import json

    result = runner.invoke(commitlint, ["lint", "--format", "json", "feat: add feature"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["valid"] is True
    assert data["errors"] == []


def test_lint_json_format_invalid_commit(runner: CliRunner) -> None:
    import json

    result = runner.invoke(commitlint, ["lint", "--format", "json", "FEAT: bad"])
    data = json.loads(result.output)
    assert data["valid"] is False
    assert len(data["errors"]) > 0


def test_lint_json_format_error_has_required_fields(runner: CliRunner) -> None:
    import json

    result = runner.invoke(commitlint, ["lint", "--format", "json", "FEAT: bad"])
    data = json.loads(result.output)
    error = data["errors"][0]
    assert "rule" in error
    assert "message" in error
    assert "severity" in error
    assert "line" in error
    assert "column" in error


# --- lint command: --quiet ---

def test_lint_quiet_suppresses_success_message(runner: CliRunner) -> None:
    result = runner.invoke(commitlint, ["lint", "--quiet", "feat: add feature"])
    assert result.output.strip() == ""
    assert result.exit_code == 0


def test_lint_quiet_still_shows_errors(runner: CliRunner) -> None:
    result = runner.invoke(commitlint, ["lint", "--quiet", "FEAT: bad"])
    assert result.exit_code == 1
    assert "type-case" in result.output


# --- lint command: --config ---

def test_lint_with_custom_config_file(runner: CliRunner, tmp_path: Path) -> None:
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
    result = runner.invoke(commitlint, ["lint", "--config", str(config), "feat: valid"])
    assert result.exit_code == 0


def test_lint_with_custom_config_rejects_unlisted_type(runner: CliRunner, tmp_path: Path) -> None:
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
    result = runner.invoke(commitlint, ["lint", "--config", str(config), "chore: something"])
    assert result.exit_code == 1


# --- lint command: --stdin ---

def test_lint_stdin_valid_commit(runner: CliRunner) -> None:
    result = runner.invoke(commitlint, ["lint", "--stdin"], input="feat: add feature\n")
    assert result.exit_code == 0


def test_lint_stdin_invalid_commit(runner: CliRunner) -> None:
    result = runner.invoke(commitlint, ["lint", "--stdin"], input="FEAT: bad commit\n")
    assert result.exit_code == 1


def test_lint_stdin_empty_input_exits_nonzero(runner: CliRunner) -> None:
    result = runner.invoke(commitlint, ["lint", "--stdin"], input="")
    assert result.exit_code == 1


# --- convert command ---

def test_convert_dry_run_prints_yaml(runner: CliRunner, tmp_path: Path) -> None:
    js_file = tmp_path / "commitlint.config.js"
    js_file.write_text("""
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {}
}
""")
    result = runner.invoke(commitlint, ["convert", "--dry-run", str(js_file)])
    assert result.exit_code == 0
    assert "@commitlint" in result.output


def test_convert_writes_output_file(runner: CliRunner, tmp_path: Path) -> None:
    js_file = tmp_path / "commitlint.config.js"
    js_file.write_text("""
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {}
}
""")
    output_file = tmp_path / "output.yaml"
    result = runner.invoke(commitlint, ["convert", str(js_file), "-o", str(output_file)])
    assert result.exit_code == 0
    assert output_file.exists()


def test_convert_default_output_filename(runner: CliRunner, tmp_path: Path) -> None:
    js_file = tmp_path / "commitlint.config.js"
    js_file.write_text("module.exports = { rules: {} }")
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(commitlint, ["convert", str(js_file)])
    assert result.exit_code == 0
