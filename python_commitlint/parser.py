import re

from python_commitlint.core.models import CommitMessage


class ConventionalCommitParser:
    HEADER_PATTERN = re.compile(
        r"^(?P<type>\w+)"
        r"(?:\((?P<scope>[^\)]+)\))?"
        r"(?P<breaking>!)?"
        r":\s*"
        r"(?P<subject>.+?)$",
        re.MULTILINE,
    )
    BREAKING_FOOTER_PATTERN = re.compile(
        r"^BREAKING[- ]CHANGE:\s*(.+)", re.MULTILINE
    )

    def parse(self, message: str) -> CommitMessage:
        lines = message.split("\n")
        header = self._extract_header(lines)
        body = self._extract_body(lines)
        footer = self._extract_footer(lines)

        match = self.HEADER_PATTERN.match(header)
        if not match:
            return CommitMessage(
                raw=message,
                header=header,
                body=body,
                footer=footer,
            )

        type_ = match.group("type") or ""
        scope = match.group("scope") or ""
        subject = match.group("subject") or ""
        breaking = match.group("breaking") == "!"

        if not breaking and self.BREAKING_FOOTER_PATTERN.search(footer):
            breaking = True

        return CommitMessage(
            raw=message,
            header=header,
            type=type_,
            scope=scope,
            subject=subject,
            body=body,
            footer=footer,
            breaking=breaking,
        )

    def _extract_header(self, lines: list[str]) -> str:
        if not lines:
            return ""
        return lines[0].strip()

    def _extract_body(self, lines: list[str]) -> str:
        if len(lines) <= 1:
            return ""

        body_lines = []
        in_body = False
        in_footer = False

        for _, line in enumerate(lines[1:], start=1):
            if not in_body and not line.strip():
                in_body = True
                continue

            if in_body and self._is_footer_line(line):
                in_footer = True
                break

            if in_body and not in_footer:
                body_lines.append(line)

        return "\n".join(body_lines).strip()

    def _extract_footer(self, lines: list[str]) -> str:
        if len(lines) <= 1:
            return ""

        footer_lines = []
        found_footer = False

        for line in reversed(lines[1:]):
            if self._is_footer_line(line) or found_footer:
                footer_lines.insert(0, line)
                found_footer = True
            elif found_footer and not line.strip():
                footer_lines.insert(0, line)
            elif found_footer:
                break

        return "\n".join(footer_lines).strip()

    def _is_footer_line(self, line: str) -> bool:
        footer_patterns = [
            r"^BREAKING[- ]CHANGE:",
            r"^[\w-]+:\s+",
            r"^[\w-]+\s+#\d+",
        ]
        return any(re.match(pattern, line) for pattern in footer_patterns)


class CommitParserFactory:
    @staticmethod
    def create() -> ConventionalCommitParser:
        return ConventionalCommitParser()
