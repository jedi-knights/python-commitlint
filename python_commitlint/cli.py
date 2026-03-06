import sys
from pathlib import Path

import click

from python_commitlint.config.converter import convert_js_to_yaml
from python_commitlint.linter import CommitLinterFactory


@click.group(name="commitlint")
def commitlint() -> None:
    pass


@commitlint.command(name="lint")
@click.argument("message", required=False)
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True),
    help="Path to configuration file (default: .commitlintrc.yaml)",
)
@click.option(
    "--stdin",
    is_flag=True,
    help="Read commit message from stdin",
)
@click.option(
    "--format",
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
    config: str | None,
    stdin: bool,
    format: str,
    quiet: bool,
) -> None:
    commit_message = _get_commit_message(message, stdin)

    if not commit_message:
        click.echo("Error: No commit message provided", err=True)
        sys.exit(1)

    assert commit_message is not None

    linter = CommitLinterFactory.create(config_path=config)
    result = linter.lint(commit_message)

    if format == "json":
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
    except Exception as e:
        click.echo(
            click.style(f"Error converting file: {e}", fg="red"),
            err=True,
        )
        sys.exit(1)


def _get_commit_message(message: str | None, stdin: bool) -> str | None:
    if stdin:
        return sys.stdin.read().strip()
    return message


def _print_text_output(result: object, quiet: bool) -> None:
    from python_commitlint.core.models import LintResult

    if not isinstance(result, LintResult):
        return
    _print_error_lines(result.errors)
    if not quiet:
        _print_warning_lines(result.warnings)
    _print_status_summary(result, quiet)


def _print_error_lines(errors: list) -> None:
    for error in errors:
        click.echo(
            f"{click.style('x', fg='red')}   "
            f"{error.message}  "
            f"{click.style(error.rule, fg='yellow')}"
        )


def _print_warning_lines(warnings: list) -> None:
    for warning in warnings:
        click.echo(
            f"{click.style('!', fg='yellow')}   "
            f"{warning.message}  "
            f"{click.style(warning.rule, fg='yellow')}"
        )


def _print_status_summary(result: object, quiet: bool) -> None:
    from python_commitlint.core.models import LintResult

    if not isinstance(result, LintResult):
        return
    if result.has_errors:
        _print_error_count(result)
        return
    if not result.has_warnings and not quiet:
        click.echo(
            click.style("Commit message is valid!", fg="green", bold=True)
        )


def _print_error_count(result: object) -> None:
    from python_commitlint.core.models import LintResult

    if not isinstance(result, LintResult):
        return
    warning_count = len(result.warnings)
    summary = f"{len(result.errors)} error(s)"
    if warning_count > 0:
        summary += f", {warning_count} warning(s)"
    click.echo(f"\n{click.style('x', fg='red')} {summary} found")


def _print_json_output(result: object) -> None:
    import json

    from python_commitlint.core.models import LintResult

    if not isinstance(result, LintResult):
        return

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
