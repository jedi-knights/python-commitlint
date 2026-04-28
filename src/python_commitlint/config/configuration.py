"""YAML configuration loading and the conventional preset."""

import copy
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from python_commitlint.core.enums import (
    RuleCondition,
    Severity,
)
from python_commitlint.core.exceptions import ConfigurationError
from python_commitlint.core.models import Configuration, RuleConfig

_LIST_SEVERITY_MAP = {0: "disabled", 1: "warning", 2: "error"}
_KNOWN_PRESETS = frozenset({"conventional"})


class ConfigurationLoader:
    """Loads commitlint configuration from YAML or the conventional preset.

    Resolution order when no explicit path is given:

    1. ``.commitlintrc.yaml`` / ``.commitlintrc.yml``
    2. ``commitlint.yaml`` / ``commitlint.yml``
    3. The built-in ``CONVENTIONAL_CONFIG``

    A YAML file may declare ``extends: conventional`` to layer custom rules
    on top of the preset.
    """

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

    def load(self, config_path: Path | None = None) -> Configuration:
        """Load and parse a :class:`Configuration`.

        Args:
            config_path: Optional explicit YAML path. When ``None``, the
                loader searches the working directory for a default file
                and falls back to the conventional preset.

        Returns:
            The fully-resolved :class:`Configuration`.

        Raises:
            ConfigurationError: If the YAML file is structurally invalid
                (e.g. ``rules`` is not a mapping, severity is unknown).
        """
        raw_config = self._load_raw_config(config_path)
        return self._parse_configuration(raw_config)

    def _load_raw_config(self, config_path: Path | None) -> dict[str, Any]:
        if config_path:
            return self._read_config_file(config_path)

        for config_file in self.DEFAULT_CONFIG_FILES:
            candidate = Path(config_file)
            if candidate.exists():
                return self._read_config_file(candidate)

        return copy.deepcopy(self.CONVENTIONAL_CONFIG)

    def _read_config_file(self, path: Path) -> dict[str, Any]:
        yaml = YAML()
        yaml.preserve_quotes = True
        with path.open("r") as f:
            config = yaml.load(f) or {}

        if "extends" in config:
            extends = config["extends"]
            if isinstance(extends, str):
                extends = [extends]

            unknown = [p for p in extends if p not in _KNOWN_PRESETS]
            if unknown:
                raise ConfigurationError(
                    f"unknown preset(s) in 'extends': {unknown!r} "
                    f"(supported: {sorted(_KNOWN_PRESETS)})"
                )

            if "conventional" in extends:
                base_config = copy.deepcopy(self.CONVENTIONAL_CONFIG)
                base_config["rules"].update(config.get("rules", {}))
                return base_config

        return config

    def _parse_configuration(self, raw_config: dict[str, Any]) -> Configuration:
        raw_rules = raw_config.get("rules", {})
        if not isinstance(raw_rules, dict):
            raise ConfigurationError(
                f"'rules' must be a mapping, got {type(raw_rules).__name__}"
            )

        rules: dict[str, RuleConfig] = {}
        for rule_name, rule_data in raw_rules.items():
            rules[rule_name] = self._parse_rule_config(rule_name, rule_data)

        extends = raw_config.get("extends", [])
        if isinstance(extends, str):
            extends = [extends]

        return Configuration(rules=rules, extends=extends)

    def _parse_rule_config(
        self, rule_name: str, rule_data: dict[str, Any] | list[Any]
    ) -> RuleConfig:
        if isinstance(rule_data, list):
            return self._parse_list_rule(rule_name, rule_data)
        if isinstance(rule_data, dict):
            return self._parse_dict_rule(rule_name, rule_data)
        raise ConfigurationError(
            f"{rule_name}: rule must be a mapping or list, "
            f"got {type(rule_data).__name__}"
        )

    def _parse_list_rule(
        self, rule_name: str, rule_data: list[Any]
    ) -> RuleConfig:
        if not rule_data:
            raise ConfigurationError(
                f"{rule_name}: rule list must not be empty"
            )
        severity_level = rule_data[0]
        severity_str = _LIST_SEVERITY_MAP.get(severity_level)
        if severity_str is None:
            raise ConfigurationError(
                f"{rule_name}: unknown severity level {severity_level!r} "
                f"(expected 0, 1, or 2)"
            )
        severity = Severity(severity_str)
        condition = self._parse_condition(
            rule_name, rule_data[1] if len(rule_data) > 1 else "always"
        )
        value = rule_data[2] if len(rule_data) > 2 else None
        return RuleConfig(severity=severity, condition=condition, value=value)

    def _parse_dict_rule(
        self, rule_name: str, rule_data: dict[str, Any]
    ) -> RuleConfig:
        try:
            severity = Severity(rule_data.get("severity", "error"))
        except ValueError as e:
            raise ConfigurationError(
                f"{rule_name}: invalid severity {rule_data.get('severity')!r}"
            ) from e
        condition = self._parse_condition(
            rule_name, rule_data.get("condition", "always")
        )
        value = rule_data.get("value")
        return RuleConfig(severity=severity, condition=condition, value=value)

    def _parse_condition(self, rule_name: str, value: Any) -> RuleCondition:
        try:
            return RuleCondition(value)
        except ValueError as e:
            raise ConfigurationError(
                f"{rule_name}: invalid condition {value!r} "
                f"(expected 'always' or 'never')"
            ) from e


class ConfigurationLoaderFactory:
    """Constructs :class:`ConfigurationLoader` instances."""

    @staticmethod
    def create() -> ConfigurationLoader:
        """Return a default :class:`ConfigurationLoader`."""
        return ConfigurationLoader()
