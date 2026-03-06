import re

from python_commitlint.enums import CaseType


class CaseValidator:
    @staticmethod
    def is_lower_case(text: str) -> bool:
        return text == text.lower() and not text[0].isupper()

    @staticmethod
    def is_upper_case(text: str) -> bool:
        return text == text.upper() and text.isupper()

    @staticmethod
    def is_camel_case(text: str) -> bool:
        if not text:
            return False
        pattern = r"^[a-z][a-zA-Z0-9]*$"
        return bool(re.match(pattern, text))

    @staticmethod
    def is_kebab_case(text: str) -> bool:
        pattern = r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$"
        return bool(re.match(pattern, text))

    @staticmethod
    def is_pascal_case(text: str) -> bool:
        if not text:
            return False
        pattern = r"^[A-Z][a-zA-Z0-9]*$"
        return bool(re.match(pattern, text))

    @staticmethod
    def is_sentence_case(text: str) -> bool:
        if not text:
            return False
        return text[0].isupper() and text[1:] == text[1:].lower()

    @staticmethod
    def is_snake_case(text: str) -> bool:
        pattern = r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$"
        return bool(re.match(pattern, text))

    @staticmethod
    def is_start_case(text: str) -> bool:
        if not text:
            return False
        words = text.split()
        return all(word[0].isupper() for word in words if word)

    @staticmethod
    def validate(text: str, case_type: CaseType) -> bool:
        validators = {
            CaseType.LOWER_CASE: CaseValidator.is_lower_case,
            CaseType.UPPER_CASE: CaseValidator.is_upper_case,
            CaseType.CAMEL_CASE: CaseValidator.is_camel_case,
            CaseType.KEBAB_CASE: CaseValidator.is_kebab_case,
            CaseType.PASCAL_CASE: CaseValidator.is_pascal_case,
            CaseType.SENTENCE_CASE: CaseValidator.is_sentence_case,
            CaseType.SNAKE_CASE: CaseValidator.is_snake_case,
            CaseType.START_CASE: CaseValidator.is_start_case,
        }
        validator = validators.get(case_type)
        if not validator:
            return False
        return validator(text)
