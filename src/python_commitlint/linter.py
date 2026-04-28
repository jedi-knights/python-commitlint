"""The commit linter — orchestrates parsing, rule dispatch, and aggregation."""

from pathlib import Path

from python_commitlint.config.configuration import (
    ConfigurationLoaderFactory,
)
from python_commitlint.core.enums import Severity
from python_commitlint.core.models import (
    CommitMessage,
    Configuration,
    LintResult,
    RuleConfig,
    ValidationError,
)
from python_commitlint.core.protocols import (
    CommitParserProtocol,
    ConfigurationLoaderProtocol,
)
from python_commitlint.parser import CommitParserFactory
from python_commitlint.rules.registry import (
    RuleRegistry,
    RuleRegistryFactory,
)


def _categorize_violation(
    violation: ValidationError,
    errors: list[ValidationError],
    warnings: list[ValidationError],
) -> None:
    """Append a violation to the matching bucket based on severity.

    Args:
        violation: The validation error produced by a rule.
        errors: Mutable list that receives ``ERROR``-severity violations.
        warnings: Mutable list that receives ``WARNING``-severity violations.

    DISABLED violations are ignored — neither bucket receives them.
    """
    if violation.severity == Severity.ERROR:
        errors.append(violation)
    elif violation.severity == Severity.WARNING:
        warnings.append(violation)


class CommitLinter:
    """Validates a commit message against a configured rule set.

    The linter is constructed with all of its collaborators (parser, rule
    registry, configuration loader) injected via :class:`CommitLinterFactory`
    so it can be tested in isolation. Configuration is loaded eagerly in
    ``__init__`` so the linter is reentrant.
    """

    def __init__(
        self,
        parser: CommitParserProtocol,
        rule_registry: RuleRegistry,
        config_loader: ConfigurationLoaderProtocol,
        config_path: Path | None = None,
    ) -> None:
        """Initialize the linter and load its configuration.

        Args:
            parser: Parser used to turn raw messages into :class:`CommitMessage`.
            rule_registry: Registry the linter uses to look rules up by name.
            config_loader: Loader that produces the resolved configuration.
            config_path: Optional explicit configuration path.
        """
        self._parser = parser
        self._rule_registry = rule_registry
        self._configuration: Configuration = config_loader.load(config_path)

    def lint(self, message: str) -> LintResult:
        """Validate ``message`` against the configured rules.

        Merge commits (first line beginning ``Merge ``) are short-circuited
        as valid without applying any rules.

        Args:
            message: Raw commit message text.

        Returns:
            A :class:`LintResult` summarizing errors, warnings, and validity.
        """
        if self._is_merge_commit(message):
            return LintResult(valid=True, errors=[], warnings=[])

        commit = self._parser.parse(message)
        errors, warnings = self._collect_violations(commit)
        return LintResult(valid=not errors, errors=errors, warnings=warnings)

    def _collect_violations(
        self, commit: CommitMessage
    ) -> tuple[list[ValidationError], list[ValidationError]]:
        errors: list[ValidationError] = []
        warnings: list[ValidationError] = []
        for rule_name, rule_config in self._configuration.rules.items():
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
        first_line = message.split("\n", 1)[0].strip()
        return first_line.startswith("Merge ")


class CommitLinterFactory:
    """Constructs :class:`CommitLinter` instances with sensible defaults."""

    @staticmethod
    def create(
        parser: CommitParserProtocol | None = None,
        rule_registry: RuleRegistry | None = None,
        config_loader: ConfigurationLoaderProtocol | None = None,
        config_path: Path | None = None,
    ) -> CommitLinter:
        """Build a :class:`CommitLinter` wired with default collaborators.

        Any collaborator can be overridden — useful for tests or for
        embedding python-commitlint inside a larger toolchain.

        Args:
            parser: Optional parser; defaults to :class:`ConventionalCommitParser`.
            rule_registry: Optional registry; defaults to one populated with
                every built-in rule.
            config_loader: Optional loader; defaults to :class:`ConfigurationLoader`.
            config_path: Optional explicit path passed through to the loader.

        Returns:
            A ready-to-use :class:`CommitLinter`.
        """
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
