from python_commitlint.configuration import (
    ConfigurationLoader,
    ConfigurationLoaderFactory,
)
from python_commitlint.enums import Severity
from python_commitlint.models import (
    CommitMessage,
    Configuration,
    LintResult,
    RuleConfig,
    ValidationError,
)
from python_commitlint.parser import (
    CommitParserFactory,
    ConventionalCommitParser,
)
from python_commitlint.protocols import (
    CommitParserProtocol,
    ConfigurationLoaderProtocol,
)
from python_commitlint.rule_registry import (
    RuleRegistry,
    RuleRegistryFactory,
)


def _categorize_violation(
    violation: ValidationError,
    errors: list[ValidationError],
    warnings: list[ValidationError],
) -> None:
    if violation.severity == Severity.ERROR:
        errors.append(violation)
    elif violation.severity == Severity.WARNING:
        warnings.append(violation)


class CommitLinter:
    def __init__(
        self,
        parser: CommitParserProtocol,
        rule_registry: RuleRegistry,
        config_loader: ConfigurationLoaderProtocol,
        config_path: str | None = None,
    ) -> None:
        self._parser = parser
        self._rule_registry = rule_registry
        self._config_loader = config_loader
        self._config_path = config_path
        self._configuration: Configuration | None = None

    def lint(self, message: str) -> LintResult:
        if self._is_merge_commit(message):
            return LintResult(valid=True, errors=[], warnings=[])

        if self._configuration is None:
            self._configuration = self._config_loader.load(self._config_path)

        commit = self._parser.parse(message)
        errors, warnings = self._collect_violations(commit)
        return LintResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

    def _collect_violations(
        self, commit: CommitMessage
    ) -> tuple[list[ValidationError], list[ValidationError]]:
        errors: list[ValidationError] = []
        warnings: list[ValidationError] = []
        for rule_name, rule_config in self._configuration.rules.items():  # type: ignore[union-attr]
            self._apply_rule(rule_name, rule_config, commit, errors, warnings)
        return errors, warnings

    def _apply_rule(
        self,
        rule_name: str,
        rule_config: RuleConfig,
        commit: CommitMessage,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        if rule_config.severity == Severity.DISABLED:
            return
        rule = self._rule_registry.get(rule_name)
        if not rule:
            return
        violation = rule.validate(commit, rule_config)
        if violation:
            _categorize_violation(violation, errors, warnings)

    def _is_merge_commit(self, message: str) -> bool:
        first_line = message.split("\n")[0].strip()
        return first_line.startswith("Merge ") or first_line.startswith(
            "Merge branch "
        )


class CommitLinterFactory:
    @staticmethod
    def create(
        parser: ConventionalCommitParser | None = None,
        rule_registry: RuleRegistry | None = None,
        config_loader: ConfigurationLoader | None = None,
        config_path: str | None = None,
    ) -> CommitLinter:
        if parser is None:
            parser = CommitParserFactory.create()

        if rule_registry is None:
            rule_registry = RuleRegistryFactory.create_with_default_rules()

        if config_loader is None:
            config_loader = ConfigurationLoaderFactory.create()

        return CommitLinter(
            parser=parser,
            rule_registry=rule_registry,
            config_loader=config_loader,
            config_path=config_path,
        )
