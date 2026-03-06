import pytest

from python_commitlint.linter import CommitLinter, CommitLinterFactory
from python_commitlint.parser import ConventionalCommitParser


@pytest.fixture
def parser() -> ConventionalCommitParser:
    return ConventionalCommitParser()


@pytest.fixture
def linter() -> CommitLinter:
    return CommitLinterFactory.create()
