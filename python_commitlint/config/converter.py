import re
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML


class CommitlintConfigConverter:
    SEVERITY_MAP = {
        0: "disabled",
        1: "warning",
        2: "error",
    }

    REVERSE_SEVERITY_MAP = {
        "disabled": 0,
        "warning": 1,
        "error": 2,
    }

    def js_to_yaml(self, js_content: str) -> str:
        config = self._parse_js_config(js_content)
        return self._generate_yaml(config)

    def _parse_js_config(self, js_content: str) -> dict[str, Any]:
        config: dict[str, Any] = {"extends": [], "rules": {}}

        extends_match = re.search(
            r"extends\s*:\s*\[(.*?)\]", js_content, re.DOTALL
        )
        if extends_match:
            extends_str = extends_match.group(1)
            extends_list = re.findall(r"['\"]([^'\"]+)['\"]", extends_str)
            config["extends"] = extends_list
        else:
            extends_match = re.search(
                r"extends\s*:\s*['\"]([^'\"]+)['\"]", js_content
            )
            if extends_match:
                config["extends"] = [extends_match.group(1)]

        rules_match = re.search(r"rules\s*:\s*\{(.*?)\}", js_content, re.DOTALL)
        if rules_match:
            rules_str = rules_match.group(1)
            config["rules"] = self._parse_rules(rules_str)

        return config

    def _parse_rules(self, rules_str: str) -> dict[str, Any]:
        rules: dict[str, Any] = {}

        rule_pattern = (
            r"(['\"]?)(\w+(?:-\w+)*)\1\s*:\s*(\[.*?\]|\d+|['\"][^'\"]*['\"])"
        )
        matches = re.finditer(rule_pattern, rules_str, re.DOTALL)

        for match in matches:
            rule_name = match.group(2)
            rule_value_str = match.group(3).strip()

            if rule_value_str.startswith("["):
                rule_value = self._parse_array(rule_value_str)
            elif rule_value_str.isdigit():
                rule_value = [int(rule_value_str), "always"]
            else:
                rule_value = rule_value_str.strip("'\"")

            rules[rule_name] = rule_value

        return rules

    def _parse_array(self, array_str: str) -> list[Any]:
        array_str = array_str.strip("[]").strip()
        if not array_str:
            return []

        result: list[Any] = []
        current = ""
        depth = 0
        in_string = False
        string_char = None

        for char in array_str:
            in_string, string_char = self._handle_string_state(
                char, in_string, string_char
            )
            if string_char == "skip":
                continue

            if not in_string:
                should_continue = self._handle_special_chars(
                    char, depth, current, result
                )
                if should_continue[0]:
                    depth = should_continue[1]
                    current = should_continue[2]
                    continue
                depth = should_continue[1]

            current += char

        if current.strip():
            result.append(self._parse_value(current.strip()))

        return result

    def _handle_string_state(
        self, char: str, in_string: bool, string_char: str | None
    ) -> tuple[bool, str | None]:
        if char in ("'", '"') and not in_string:
            return True, "skip"
        if char == string_char and in_string:
            return False, "skip"
        return in_string, string_char

    def _handle_special_chars(
        self, char: str, depth: int, current: str, result: list[Any]
    ) -> tuple[bool, int, str]:
        if char == "[":
            return False, depth + 1, current
        if char == "]":
            return False, depth - 1, current
        if char == "," and depth == 0:
            value = current.strip()
            if value:
                result.append(self._parse_value(value))
            return True, depth, ""
        return False, depth, current

    def _parse_value(self, value: str) -> Any:
        value = value.strip()

        if value.startswith("["):
            return self._parse_array(value)

        if value.startswith("'") or value.startswith('"'):
            return value.strip("'\"")

        if value.isdigit():
            return int(value)

        if value == "true":
            return True
        if value == "false":
            return False

        return value

    def _generate_yaml(self, config: dict[str, Any]) -> str:
        yaml_config: dict[str, Any] = {}

        if config.get("extends"):
            yaml_config["extends"] = config["extends"]

        if config.get("rules"):
            yaml_config["rules"] = {}
            for rule_name, rule_value in config["rules"].items():
                yaml_config["rules"][rule_name] = rule_value

        yaml = YAML()
        yaml.default_flow_style = False
        yaml.allow_unicode = True
        yaml.width = 80

        from io import StringIO

        stream = StringIO()
        yaml.dump(yaml_config, stream)
        return stream.getvalue()


def convert_js_to_yaml(
    input_path: Path, output_path: Path | None = None
) -> str:
    converter = CommitlintConfigConverter()

    with open(input_path) as f:
        js_content = f.read()

    yaml_content = converter.js_to_yaml(js_content)

    if output_path:
        with open(output_path, "w") as f:
            f.write(yaml_content)

    return yaml_content
