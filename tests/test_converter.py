from pathlib import Path

from python_commitlint.config.converter import (
    CommitlintConfigConverter,
    convert_js_to_yaml,
)

JS_CONFIG_SIMPLE = """
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [2, 'always', ['feat', 'fix', 'docs']],
    'header-max-length': [2, 'always', 72],
  }
}
"""

JS_CONFIG_SINGLE_EXTEND = """
module.exports = {
  extends: '@commitlint/config-conventional',
  rules: {}
}
"""

JS_CONFIG_NO_EXTENDS = """
module.exports = {
  rules: {
    'type-empty': [2, 'never'],
  }
}
"""


def test_converter_parses_extends_array() -> None:
    converter = CommitlintConfigConverter()
    result = converter.js_to_yaml(JS_CONFIG_SIMPLE)
    assert "@commitlint/config-conventional" in result


def test_converter_parses_single_extend_string() -> None:
    converter = CommitlintConfigConverter()
    result = converter.js_to_yaml(JS_CONFIG_SINGLE_EXTEND)
    assert "@commitlint/config-conventional" in result


def test_converter_parses_rules() -> None:
    converter = CommitlintConfigConverter()
    result = converter.js_to_yaml(JS_CONFIG_SIMPLE)
    assert "type-enum" in result
    assert "header-max-length" in result


def test_converter_output_is_valid_yaml() -> None:
    from ruamel.yaml import YAML

    converter = CommitlintConfigConverter()
    result = converter.js_to_yaml(JS_CONFIG_SIMPLE)
    yaml = YAML()
    parsed = yaml.load(result)
    assert parsed is not None
    assert "rules" in parsed


def test_converter_handles_no_extends() -> None:
    converter = CommitlintConfigConverter()
    result = converter.js_to_yaml(JS_CONFIG_NO_EXTENDS)
    assert "type-empty" in result


def test_convert_js_to_yaml_reads_file_and_returns_string(
    tmp_path: Path,
) -> None:
    js_file = tmp_path / "commitlint.config.js"
    js_file.write_text(JS_CONFIG_SIMPLE)
    result = convert_js_to_yaml(js_file)
    assert isinstance(result, str)
    assert "type-enum" in result


def test_convert_js_to_yaml_writes_output_file(tmp_path: Path) -> None:
    js_file = tmp_path / "commitlint.config.js"
    js_file.write_text(JS_CONFIG_SIMPLE)
    output_file = tmp_path / ".commitlintrc.yaml"
    convert_js_to_yaml(js_file, output_file)
    assert output_file.exists()
    content = output_file.read_text()
    assert "type-enum" in content


def test_convert_js_to_yaml_no_output_path_does_not_write(
    tmp_path: Path,
) -> None:
    js_file = tmp_path / "commitlint.config.js"
    js_file.write_text(JS_CONFIG_SIMPLE)
    result = convert_js_to_yaml(js_file)
    output = tmp_path / ".commitlintrc.yaml"
    assert not output.exists()
    assert result


def test_converter_severity_map_values() -> None:
    assert CommitlintConfigConverter.SEVERITY_MAP[0] == "disabled"
    assert CommitlintConfigConverter.SEVERITY_MAP[1] == "warning"
    assert CommitlintConfigConverter.SEVERITY_MAP[2] == "error"


def test_converter_preserves_nested_array_values() -> None:
    js = """
    module.exports = {
      rules: {
        'type-enum': [2, 'always', ['feat', 'fix', 'docs']],
      }
    }
    """
    converter = CommitlintConfigConverter()
    parsed = converter._parse_js_config(js)
    assert parsed["rules"]["type-enum"] == [
        2,
        "always",
        ["feat", "fix", "docs"],
    ]
