import os
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from python_commitlint.enums import (
    RuleCondition,
    Severity,
)
from python_commitlint.models import Configuration, RuleConfig


class ConfigurationLoader:
    DEFAULT_CONFIG_FILES = [
        ".commitlintrc.yaml",
        ".commitlintrc.yml",
        "commitlint.yaml",
        "commitlint.yml",
    ]

    CONVENTIONAL_CONFIG = {
        "rules": {
            "body-leading-blank": {
                "severity": "warning",
                "condition": "always",
            },
            "body-max-line-length": {
                "severity": "error",
                "condition": "always",
                "value": 100,
            },
            "footer-leading-blank": {
                "severity": "warning",
                "condition": "always",
            },
            "footer-max-line-length": {
                "severity": "error",
                "condition": "always",
                "value": 100,
            },
            "header-max-length": {
                "severity": "error",
                "condition": "always",
                "value": 100,
            },
            "header-trim": {"severity": "error", "condition": "always"},
            "subject-case": {
                "severity": "error",
                "condition": "never",
                "value": [
                    "sentence-case",
                    "start-case",
                    "pascal-case",
                    "upper-case",
                ],
            },
            "subject-empty": {"severity": "error", "condition": "never"},
            "subject-full-stop": {
                "severity": "error",
                "condition": "never",
                "value": ".",
            },
            "type-case": {
                "severity": "error",
                "condition": "always",
                "value": "lower-case",
            },
            "type-empty": {"severity": "error", "condition": "never"},
            "type-enum": {
                "severity": "error",
                "condition": "always",
                "value": [
                    "build",
                    "chore",
                    "ci",
                    "docs",
                    "feat",
                    "fix",
                    "perf",
                    "refactor",
                    "revert",
                    "style",
                    "test",
                ],
            },
        }
    }

    def load(self, config_path: str | None = None) -> Configuration:
        raw_config = self._load_raw_config(config_path)
        return self._parse_configuration(raw_config)

    def _load_raw_config(self, config_path: str | None) -> dict[str, Any]:
        if config_path:
            return self._read_config_file(config_path)

        for config_file in self.DEFAULT_CONFIG_FILES:
            if os.path.exists(config_file):
                return self._read_config_file(config_file)

        return self.CONVENTIONAL_CONFIG

    def _read_config_file(self, path: str) -> dict[str, Any]:
        yaml = YAML()
        yaml.preserve_quotes = True
        with Path(path).open("r") as f:
            config = yaml.load(f) or {}

        if "extends" in config:
            extends = config["extends"]
            if isinstance(extends, str):
                extends = [extends]

            for preset in extends:
                if preset == "conventional":
                    base_config = self.CONVENTIONAL_CONFIG.copy()
                    base_config["rules"].update(config.get("rules", {}))
                    return base_config

        return config

    def _parse_configuration(self, raw_config: dict[str, Any]) -> Configuration:
        rules = {}
        for rule_name, rule_data in raw_config.get("rules", {}).items():
            rules[rule_name] = self._parse_rule_config(rule_data)

        extends = raw_config.get("extends", [])
        if isinstance(extends, str):
            extends = [extends]

        return Configuration(rules=rules, extends=extends)

    def _parse_rule_config(
        self, rule_data: dict[str, Any] | list[Any]
    ) -> RuleConfig:
        if isinstance(rule_data, list):
            severity_map = {0: "disabled", 1: "warning", 2: "error"}
            severity_level = rule_data[0] if len(rule_data) > 0 else 2
            severity = Severity(severity_map.get(severity_level, "error"))
            condition = (
                RuleCondition(rule_data[1])
                if len(rule_data) > 1
                else RuleCondition.ALWAYS
            )
            value = rule_data[2] if len(rule_data) > 2 else None
        else:
            severity = Severity(rule_data.get("severity", "error"))
            condition = RuleCondition(rule_data.get("condition", "always"))
            value = rule_data.get("value")

        return RuleConfig(severity=severity, condition=condition, value=value)


class ConfigurationLoaderFactory:
    @staticmethod
    def create() -> ConfigurationLoader:
        return ConfigurationLoader()
