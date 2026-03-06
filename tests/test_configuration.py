from pathlib import Path

import pytest

from python_commitlint.configuration import ConfigurationLoader
from python_commitlint.enums import RuleCondition, Severity


def test_load_default_config_when_no_file_exists(tmp_path: Path) -> None:
    import os

    original_dir = os.getcwd()
    os.chdir(tmp_path)
    try:
        loader = ConfigurationLoader()
        config = loader.load()
        assert "type-enum" in config.rules
        assert "type-case" in config.rules
        assert "subject-empty" in config.rules
    finally:
        os.chdir(original_dir)


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
    config = loader.load(str(config_file))

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
    config = loader.load(str(config_file))

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
    config = loader.load(str(config_file))

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
    config = loader.load(str(config_file))

    assert config.rules["type-enum"].severity == Severity.DISABLED
