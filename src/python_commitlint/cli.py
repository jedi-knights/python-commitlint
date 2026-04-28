"""Command-line entry point for python-commitlint.

Defines the ``commitlint`` Click group with two subcommands:

- ``lint`` — validate a commit message against the configured rules
- ``convert`` — translate a ``commitlint.config.js`` to ``.commitlintrc.yaml``
"""

import json
import sys
from pathlib import Path

import click

from python_commitlint.config.converter import convert_js_to_yaml
from python_commitlint.core.exceptions import ConfigurationError
from python_commitlint.core.models import LintResult, ValidationError
from python_commitlint.linter import CommitLinterFactory


@click.group(name="commitlint")
def commitlint() -> None:
    """python-commitlint command-line interface."""


@commitlint.command(name="lint")
@click.argument("message", required=False)
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to configuration file (default: .commitlintrc.yaml)",
)
@click.option(
    "--stdin",
    is_flag=True,
    help="Read commit message from stdin",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help="Suppress output except for errors",
)
def lint_command(
    message: str | None,
    config: Path | None,
    stdin: bool,
    output_format: str,
    quiet: bool,
) -> None:
    """Validate a commit message and exit non-zero on failure.

    The message can be supplied as a positional argument or read from
    stdin via ``--stdin`` (typical git ``commit-msg`` hook usage).
    """
    commit_message = _get_commit_message(message, stdin)

    if not commit_message:
        click.echo("Error: No commit message provided", err=True)
        sys.exit(1)

    try:
        linter = CommitLinterFactory.create(config_path=config)
        result = linter.lint(commit_message)
    except ConfigurationError as e:
        click.echo(click.style(f"Configuration error: {e}", fg="red"), err=True)
        sys.exit(1)

    if output_format == "json":
        _print_json_output(result)
    else:
        _print_text_output(result, quiet)

    sys.exit(0 if result.valid else 1)


@commitlint.command(name="convert")
@click.argument(
    "input_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option(
    "-o",
    "--output",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Output file path (default: .commitlintrc.yaml)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Print the converted configuration without writing to file",
)
def convert_command(
    input_file: Path,
    output: Path | None,
    dry_run: bool,
) -> None:
    """Convert a ``commitlint.config.js`` file to ``.commitlintrc.yaml``.

    With ``--dry-run`` the YAML is written to stdout; otherwise it is
    written to ``--output`` (or ``.commitlintrc.yaml`` by default).
    """
    if output is None and not dry_run:
        output = Path(".commitlintrc.yaml")

    try:
        if dry_run:
            yaml_content = convert_js_to_yaml(input_file)
            click.echo(yaml_content)
        else:
            yaml_content = convert_js_to_yaml(input_file, output)
            click.echo(
                click.style(
                    f"Successfully converted {input_file} to {output}",
                    fg="green",
                    bold=True,
                )
            )
    except (OSError, ValueError) as e:
        # Catch the user-facing failure modes (file I/O, decode/encode
        # errors) and let any other exception propagate as a real
        # traceback — those would indicate an internal bug.
        click.echo(
            click.style(
                f"Error converting file ({type(e).__name__}): {e}", fg="red"
            ),
            err=True,
        )
        sys.exit(1)


def _get_commit_message(message: str | None, stdin: bool) -> str | None:
    if stdin:
        # An empty stdin returns "" — falsy, so the caller treats it as
        # "no message provided" and exits with an error.
        return sys.stdin.read().strip()
    return message


def _print_text_output(result: LintResult, quiet: bool) -> None:
    _print_error_lines(result.errors)
    if not quiet:
        _print_warning_lines(result.warnings)
    _print_status_summary(result, quiet)


def _print_error_lines(errors: list[ValidationError]) -> None:
    for error in errors:
        click.echo(
            f"{click.style('x', fg='red')}   "
            f"{error.message}  "
            f"{click.style(error.rule, fg='yellow')}"
        )


def _print_warning_lines(warnings: list[ValidationError]) -> None:
    for warning in warnings:
        click.echo(
            f"{click.style('!', fg='yellow')}   "
            f"{warning.message}  "
            f"{click.style(warning.rule, fg='yellow')}"
        )


def _print_status_summary(result: LintResult, quiet: bool) -> None:
    if result.has_errors:
        _print_error_count(result)
        return
    if not result.has_warnings and not quiet:
        click.echo(
            click.style("Commit message is valid!", fg="green", bold=True)
        )


def _print_error_count(result: LintResult) -> None:
    warning_count = len(result.warnings)
    summary = f"{len(result.errors)} error(s)"
    if warning_count > 0:
        summary += f", {warning_count} warning(s)"
    click.echo(f"\n{click.style('x', fg='red')} {summary} found")


def _print_json_output(result: LintResult) -> None:
    output = {
        "valid": result.valid,
        "errors": [
            {
                "rule": error.rule,
                "message": error.message,
                "severity": error.severity.value,
                "line": error.line,
                "column": error.column,
            }
            for error in result.errors
        ],
        "warnings": [
            {
                "rule": warning.rule,
                "message": warning.message,
                "severity": warning.severity.value,
                "line": warning.line,
                "column": warning.column,
            }
            for warning in result.warnings
        ],
    }

    click.echo(json.dumps(output, indent=2))


if __name__ == "__main__":
    commitlint()
