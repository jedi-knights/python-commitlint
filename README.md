# python-commitlint

A pure-Python implementation of [commitlint](https://commitlint.js.org/) for validating [Conventional Commits](https://www.conventionalcommits.org/). No Node.js required.

[![Python](https://img.shields.io/badge/python-3.13%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Coverage](https://img.shields.io/badge/Coverage-96.0%25-brightgreen)

---

## Features

- Full [Conventional Commits](https://www.conventionalcommits.org/) specification support
- Drop-in replacement for `@commitlint/cli` and `@commitlint/config-conventional`
- YAML-based configuration — no JavaScript
- 32 built-in validation rules covering type, scope, subject, header, body, and footer
- Multiple output formats: human-readable text and JSON
- Stdin support for use as a git commit-msg hook
- JS config converter (`commitlint.config.js` → `.commitlintrc.yaml`)
- Zero Node.js dependencies

---

## Installation

```bash
pip install python-commitlint
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add python-commitlint
```

---

## Quick Start

```bash
# Validate a commit message
commitlint lint "feat: add user authentication"

# Read from stdin (git hook usage)
echo "feat: add user authentication" | commitlint lint --stdin

# Use a custom config file
commitlint lint "fix: resolve timeout" --config .commitlintrc.yaml

# Output as JSON
commitlint lint "feat: add feature" --format json
```

---

## Usage

### `commitlint lint`

```
Usage: commitlint lint [OPTIONS] [MESSAGE]

Options:
  -c, --config PATH          Path to configuration file
  --stdin                    Read commit message from stdin
  --format [text|json]       Output format (default: text)
  -q, --quiet                Suppress output except for errors
  -h, --help                 Show this message and exit
```

**Examples**

```bash
# Argument
commitlint lint "feat(api): add pagination support"

# Stdin
git log -1 --pretty=%B | commitlint lint --stdin

# Quiet mode for CI (exit code only)
commitlint lint --quiet --stdin < .git/COMMIT_EDITMSG

# JSON output for tooling
commitlint lint --format json "fix: resolve null pointer"
```

**JSON output shape**

```json
{
  "valid": false,
  "errors": [
    {
      "rule": "type-case",
      "message": "type must be lower-case",
      "severity": "error",
      "line": 1,
      "column": 0
    }
  ],
  "warnings": []
}
```

### `commitlint convert`

Converts a `commitlint.config.js` file to a `.commitlintrc.yaml` file.

```
Usage: commitlint convert [OPTIONS] INPUT_FILE

Options:
  -o, --output PATH   Output file path (default: .commitlintrc.yaml)
  --dry-run           Print converted config without writing to disk
  -h, --help          Show this message and exit
```

```bash
# Convert and write to .commitlintrc.yaml
commitlint convert commitlint.config.js

# Preview without writing
commitlint convert --dry-run commitlint.config.js

# Write to a custom path
commitlint convert commitlint.config.js -o config/commitlint.yaml
```

---

## Configuration

By default, `commitlint lint` looks for a config file in the current directory using these names (in order):

1. `.commitlintrc.yaml`
2. `.commitlintrc.yml`
3. `commitlint.yaml`
4. `commitlint.yml`

If no file is found, the built-in `conventional` preset is used.

### Using the conventional preset

```yaml
# .commitlintrc.yaml
extends: conventional
```

### Custom rules

```yaml
# .commitlintrc.yaml
extends: conventional

rules:
  type-enum:
    severity: error
    condition: always
    value:
      - feat
      - fix
      - docs
      - chore
      - hotfix

  header-max-length:
    severity: error
    condition: always
    value: 72

  scope-enum:
    severity: error
    condition: always
    value:
      - api
      - ui
      - db
      - auth
```

### Rule format

Each rule entry accepts:

| Field | Values |
|---|---|
| `severity` | `error`, `warning`, `disabled` |
| `condition` | `always`, `never` |
| `value` | rule-specific (string, number, or list) |

Rules also support the numeric array format used by the original commitlint:

```yaml
rules:
  type-enum: [2, always, [feat, fix, docs]]
  header-max-length: [2, always, 72]
```

---

## Built-in Rules

### Type
| Rule | Description |
|---|---|
| `type-empty` | Require or disallow an empty type |
| `type-case` | Enforce case style for the type |
| `type-enum` | Restrict type to an allowed set |
| `type-min-length` | Minimum character length for type |
| `type-max-length` | Maximum character length for type |

### Scope
| Rule | Description |
|---|---|
| `scope-empty` | Require or disallow an empty scope |
| `scope-case` | Enforce case style for the scope |
| `scope-enum` | Restrict scope to an allowed set |
| `scope-min-length` | Minimum character length for scope |
| `scope-max-length` | Maximum character length for scope |

### Subject
| Rule | Description |
|---|---|
| `subject-empty` | Require or disallow an empty subject |
| `subject-case` | Enforce case style for the subject |
| `subject-full-stop` | Require or disallow a trailing punctuation character |
| `subject-min-length` | Minimum character length for subject |
| `subject-max-length` | Maximum character length for subject |

### Header
| Rule | Description |
|---|---|
| `header-max-length` | Maximum character length for the header line |
| `header-min-length` | Minimum character length for the header line |
| `header-trim` | Disallow leading or trailing whitespace in the header |
| `header-full-stop` | Require or disallow a trailing punctuation character |
| `header-case` | Enforce case style for the full header |

### Body
| Rule | Description |
|---|---|
| `body-empty` | Require or disallow an empty body |
| `body-leading-blank` | Require a blank line between header and body |
| `body-max-length` | Maximum total character length for the body |
| `body-max-line-length` | Maximum character length per body line (URLs are exempt) |
| `body-min-length` | Minimum total character length for the body |
| `body-full-stop` | Require or disallow a trailing punctuation character |
| `body-case` | Enforce case style for the body |

### Footer
| Rule | Description |
|---|---|
| `footer-empty` | Require or disallow an empty footer |
| `footer-leading-blank` | Require a blank line before the footer |
| `footer-max-length` | Maximum total character length for the footer |
| `footer-max-line-length` | Maximum character length per footer line |
| `footer-min-length` | Minimum total character length for the footer |

---

## CI/CD Integration

### Git commit-msg hook

Create `.git/hooks/commit-msg` and make it executable:

```bash
#!/bin/sh
commitlint lint --stdin < "$1"
```

```bash
chmod +x .git/hooks/commit-msg
```

### GitHub Actions

```yaml
- name: Validate commit message
  run: git log -1 --pretty=%B | commitlint lint --stdin
```

### GitLab CI

```yaml
commitlint:
  script:
    - git log -1 --pretty=%B | commitlint lint --stdin
```

---

## Development

```bash
# Clone the repo
git clone https://github.com/jedi-knights/python-commitlint
cd python-commitlint

# Install dependencies (including dev extras)
uv sync --extra dev

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov --cov-report=term-missing

# Lint
uv run ruff check .

# Format
uv run ruff format .
```

---

## Valid Commit Examples

```
feat: add user authentication
fix(api): resolve timeout on large payloads
docs: update installation guide
chore(deps): upgrade ruamel.yaml to 0.18
refactor: extract validation logic into separate module
test: add integration tests for scope rules
ci: add GitHub Actions workflow
build!: drop support for Python 3.12
```

## Invalid Commit Examples

```
Feature: wrong type format          # type not lowercase
FEAT: uppercase type                # type must be lower-case
feat: subject ending in period.     # trailing period not allowed
feat:missing space after colon      # malformed header
just a message                      # missing type and colon
```

---

## License

[MIT](LICENSE)
