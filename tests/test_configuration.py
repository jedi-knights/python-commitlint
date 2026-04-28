from pathlib import Path

import pytest

from python_commitlint.config.configuration import ConfigurationLoader
from python_commitlint.core.enums import RuleCondition, Severity
from python_commitlint.core.exceptions import ConfigurationError


def test_load_default_config_when_no_file_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    loader = ConfigurationLoader()
    config = loader.load()
    assert "type-enum" in config.rules
    assert "type-case" in config.rules
    assert "subject-empty" in config.rules


def test_load_yaml_config_file(tmp_path: Path) -> None:
    config_content = """
rules:
  type-enum:
    severity: error
    condition: always
    value:
      - feat
      - fix
"""
    config_file = tmp_path / ".commitlintrc.yaml"
    config_file.write_text(config_content)

    loader = ConfigurationLoader()
    config = loader.load(config_file)

    assert "type-enum" in config.rules
    rule = config.rules["type-enum"]
    assert rule.severity == Severity.ERROR
    assert rule.condition == RuleCondition.ALWAYS
    assert "feat" in rule.value
    assert "fix" in rule.value


def test_load_config_with_extends_conventional(tmp_path: Path) -> None:
    config_content = """
extends: conventional
rules:
  header-max-length:
    severity: error
    condition: always
    value: 72
"""
    config_file = tmp_path / ".commitlintrc.yaml"
    config_file.write_text(config_content)

    loader = ConfigurationLoader()
    config = loader.load(config_file)

    assert "type-enum" in config.rules
    assert config.rules["header-max-length"].value == 72


def test_parse_list_format_rule_config(tmp_path: Path) -> None:
    config_content = """
rules:
  type-enum:
    - 2
    - always
    - - feat
      - fix
"""
    config_file = tmp_path / ".commitlintrc.yaml"
    config_file.write_text(config_content)

    loader = ConfigurationLoader()
    config = loader.load(config_file)

    rule = config.rules["type-enum"]
    assert rule.severity == Severity.ERROR
    assert rule.condition == RuleCondition.ALWAYS


def test_severity_disabled_parsed_correctly(tmp_path: Path) -> None:
    config_content = """
rules:
  type-enum:
    severity: disabled
    condition: always
"""
    config_file = tmp_path / ".commitlintrc.yaml"
    config_file.write_text(config_content)

    loader = ConfigurationLoader()
    config = loader.load(config_file)

    assert config.rules["type-enum"].severity == Severity.DISABLED


def test_unknown_extends_preset_raises(tmp_path: Path) -> None:
    config_file = tmp_path / ".commitlintrc.yaml"
    config_file.write_text("extends: commitlint-config-angular\nrules: {}\n")

    loader = ConfigurationLoader()
    with pytest.raises(ConfigurationError, match="unknown preset"):
        loader.load(config_file)


def test_empty_list_rule_raises(tmp_path: Path) -> None:
    config_file = tmp_path / ".commitlintrc.yaml"
    config_file.write_text("rules:\n  type-enum: []\n")

    loader = ConfigurationLoader()
    with pytest.raises(ConfigurationError, match="must not be empty"):
        loader.load(config_file)
