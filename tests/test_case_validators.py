import pytest

from python_commitlint.core.enums import CaseType
from python_commitlint.rules.case_validators import CaseValidator

# --- lower-case ---


@pytest.mark.parametrize("text", ["feat", "add new feature", "fix-bug"])
def test_is_lower_case_valid(text: str) -> None:
    assert CaseValidator.is_lower_case(text) is True


@pytest.mark.parametrize("text", ["Feat", "ADD", "Fix-Bug"])
def test_is_lower_case_invalid(text: str) -> None:
    assert CaseValidator.is_lower_case(text) is False


# --- upper-case ---


@pytest.mark.parametrize("text", ["FEAT", "ADD NEW FEATURE", "FIX-BUG"])
def test_is_upper_case_valid(text: str) -> None:
    assert CaseValidator.is_upper_case(text) is True


@pytest.mark.parametrize("text", ["feat", "Add", "fix-bug"])
def test_is_upper_case_invalid(text: str) -> None:
    assert CaseValidator.is_upper_case(text) is False


# --- camel-case ---


@pytest.mark.parametrize("text", ["feat", "addNewFeature", "fixBug"])
def test_is_camel_case_valid(text: str) -> None:
    assert CaseValidator.is_camel_case(text) is True


@pytest.mark.parametrize("text", ["Feat", "AddNewFeature", "fix-bug", ""])
def test_is_camel_case_invalid(text: str) -> None:
    assert CaseValidator.is_camel_case(text) is False


# --- kebab-case ---


@pytest.mark.parametrize("text", ["feat", "add-new-feature", "fix-bug"])
def test_is_kebab_case_valid(text: str) -> None:
    assert CaseValidator.is_kebab_case(text) is True


@pytest.mark.parametrize(
    "text", ["Feat", "add_new_feature", "Add-New", "feat feat"]
)
def test_is_kebab_case_invalid(text: str) -> None:
    assert CaseValidator.is_kebab_case(text) is False


# --- pascal-case ---


@pytest.mark.parametrize("text", ["Feat", "AddNewFeature", "FixBug"])
def test_is_pascal_case_valid(text: str) -> None:
    assert CaseValidator.is_pascal_case(text) is True


@pytest.mark.parametrize("text", ["feat", "add-new-feature", "fixBug", ""])
def test_is_pascal_case_invalid(text: str) -> None:
    assert CaseValidator.is_pascal_case(text) is False


# --- sentence-case ---


@pytest.mark.parametrize("text", ["Feat", "Add new feature", "Fix bug"])
def test_is_sentence_case_valid(text: str) -> None:
    assert CaseValidator.is_sentence_case(text) is True


@pytest.mark.parametrize(
    "text", ["feat", "ADD NEW FEATURE", "add New feature", ""]
)
def test_is_sentence_case_invalid(text: str) -> None:
    assert CaseValidator.is_sentence_case(text) is False


# --- snake-case ---


@pytest.mark.parametrize("text", ["feat", "add_new_feature", "fix_bug"])
def test_is_snake_case_valid(text: str) -> None:
    assert CaseValidator.is_snake_case(text) is True


@pytest.mark.parametrize(
    "text", ["Feat", "add-new-feature", "Add_New", "feat feat"]
)
def test_is_snake_case_invalid(text: str) -> None:
    assert CaseValidator.is_snake_case(text) is False


# --- start-case ---


@pytest.mark.parametrize("text", ["Feat", "Add New Feature", "Fix Bug"])
def test_is_start_case_valid(text: str) -> None:
    assert CaseValidator.is_start_case(text) is True


@pytest.mark.parametrize("text", ["feat", "add new feature", ""])
def test_is_start_case_invalid(text: str) -> None:
    assert CaseValidator.is_start_case(text) is False


# --- validate dispatch ---


@pytest.mark.parametrize(
    "text,case_type,expected",
    [
        ("feat", CaseType.LOWER_CASE, True),
        ("FEAT", CaseType.UPPER_CASE, True),
        ("addFeat", CaseType.CAMEL_CASE, True),
        ("add-feat", CaseType.KEBAB_CASE, True),
        ("AddFeat", CaseType.PASCAL_CASE, True),
        ("Add feat", CaseType.SENTENCE_CASE, True),
        ("add_feat", CaseType.SNAKE_CASE, True),
        ("Add Feat", CaseType.START_CASE, True),
        ("FEAT", CaseType.LOWER_CASE, False),
        ("feat", CaseType.UPPER_CASE, False),
    ],
)
def test_validate_dispatch(
    text: str, case_type: CaseType, expected: bool
) -> None:
    assert CaseValidator.validate(text, case_type) is expected
