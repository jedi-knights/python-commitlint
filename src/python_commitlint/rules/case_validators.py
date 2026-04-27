"""Case-style validators (lower, upper, camel, pascal, kebab, etc.)."""

import re
from collections.abc import Callable
from typing import ClassVar

from python_commitlint.core.enums import CaseType


class CaseValidator:
    """Static helpers and a dispatcher for checking text against a case style.

    Each ``is_<style>_case`` method returns ``True`` when the input matches
    the named style. :meth:`validate` provides a single dispatch entry
    point keyed by :class:`CaseType`.
    """

    @staticmethod
    def is_lower_case(text: str) -> bool:
        """Return True when ``text`` is non-empty and entirely lower case."""
        if not text:
            return False
        return text == text.lower()

    @staticmethod
    def is_upper_case(text: str) -> bool:
        """Return True when ``text`` is entirely upper case."""
        return text == text.upper() and text.isupper()

    @staticmethod
    def is_camel_case(text: str) -> bool:
        """Return True when ``text`` matches camelCase (lowercase first char)."""
        if not text:
            return False
        pattern = r"^[a-z][a-zA-Z0-9]*$"
        return bool(re.match(pattern, text))

    @staticmethod
    def is_kebab_case(text: str) -> bool:
        """Return True when ``text`` matches kebab-case (hyphen separated)."""
        pattern = r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$"
        return bool(re.match(pattern, text))

    @staticmethod
    def is_pascal_case(text: str) -> bool:
        """Return True when ``text`` matches PascalCase (uppercase first char)."""
        if not text:
            return False
        pattern = r"^[A-Z][a-zA-Z0-9]*$"
        return bool(re.match(pattern, text))

    @staticmethod
    def is_sentence_case(text: str) -> bool:
        """Return True when only the first character of ``text`` is uppercase."""
        if not text:
            return False
        return text[0].isupper() and text[1:] == text[1:].lower()

    @staticmethod
    def is_snake_case(text: str) -> bool:
        """Return True when ``text`` matches snake_case (underscore separated)."""
        pattern = r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$"
        return bool(re.match(pattern, text))

    @staticmethod
    def is_start_case(text: str) -> bool:
        """Return True when every word in ``text`` starts with an uppercase letter."""
        if not text:
            return False
        words = text.split()
        return all(word[0].isupper() for word in words if word)

    # Defined inline to avoid a two-phase init. `staticmethod` objects are
    # callable in Python 3.10+, so the dispatcher can store and invoke
    # them directly.
    _VALIDATORS: ClassVar[dict[CaseType, Callable[[str], bool]]] = {
        CaseType.LOWER_CASE: is_lower_case,
        CaseType.UPPER_CASE: is_upper_case,
        CaseType.CAMEL_CASE: is_camel_case,
        CaseType.KEBAB_CASE: is_kebab_case,
        CaseType.PASCAL_CASE: is_pascal_case,
        CaseType.SENTENCE_CASE: is_sentence_case,
        CaseType.SNAKE_CASE: is_snake_case,
        CaseType.START_CASE: is_start_case,
    }

    @classmethod
    def validate(cls, text: str, case_type: CaseType) -> bool:
        """Return True when ``text`` matches the requested ``case_type``.

        Args:
            text: The text to validate.
            case_type: The expected case style.

        Returns:
            True on a match, False otherwise (including when ``case_type``
            is unknown).
        """
        validator = cls._VALIDATORS.get(case_type)
        if not validator:
            return False
        return validator(text)
