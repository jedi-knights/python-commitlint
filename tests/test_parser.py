import pytest

from python_commitlint.parser import ConventionalCommitParser


@pytest.mark.parametrize(
    "message,expected_type,expected_scope,expected_subject",
    [
        ("feat: add new feature", "feat", "", "add new feature"),
        (
            "fix(api): resolve timeout issue",
            "fix",
            "api",
            "resolve timeout issue",
        ),
        (
            "docs: update installation guide",
            "docs",
            "",
            "update installation guide",
        ),
        (
            "chore(deps): upgrade dependencies",
            "chore",
            "deps",
            "upgrade dependencies",
        ),
        ("feat!: breaking change", "feat", "", "breaking change"),
        ("fix(api)!: breaking fix", "fix", "api", "breaking fix"),
    ],
)
def test_parse_conventional_commit(
    parser: ConventionalCommitParser,
    message: str,
    expected_type: str,
    expected_scope: str,
    expected_subject: str,
) -> None:
    result = parser.parse(message)
    assert result.type == expected_type
    assert result.scope == expected_scope
    assert result.subject == expected_subject


def test_parse_invalid_commit(parser: ConventionalCommitParser) -> None:
    result = parser.parse("not a conventional commit")
    assert result.type == ""
    assert result.subject == ""
    assert result.header == "not a conventional commit"


def test_parse_breaking_change_via_exclamation(
    parser: ConventionalCommitParser,
) -> None:
    result = parser.parse("feat!: breaking change")
    assert result.breaking is True


def test_parse_breaking_change_via_footer(
    parser: ConventionalCommitParser,
) -> None:
    message = (
        "feat: add feature\n\nSome body\n\nBREAKING CHANGE: something changed"
    )
    result = parser.parse(message)
    assert result.breaking is True


def test_parse_body(parser: ConventionalCommitParser) -> None:
    message = "feat: add feature\n\nThis is the body\nwith multiple lines"
    result = parser.parse(message)
    assert result.body == "This is the body\nwith multiple lines"


def test_parse_empty_message(parser: ConventionalCommitParser) -> None:
    result = parser.parse("")
    assert result.type == ""
    assert result.header == ""


def test_parse_merge_commit(parser: ConventionalCommitParser) -> None:
    result = parser.parse("Merge branch 'main' into feature/my-branch")
    assert result.type == ""
    assert result.header == "Merge branch 'main' into feature/my-branch"
