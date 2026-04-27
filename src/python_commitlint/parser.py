"""Parses raw commit message text into structured :class:`CommitMessage` values."""

import re

from python_commitlint.core.models import CommitMessage


class ConventionalCommitParser:
    """Parses Conventional Commits messages into :class:`CommitMessage`.

    The parser extracts type, optional scope, breaking-change marker, and
    subject from the header line, and separates the body from the footer
    block when present. Messages that do not match the conventional pattern
    are returned with empty type and subject but with the original raw
    text and header preserved.
    """

    HEADER_PATTERN = re.compile(
        r"^(?P<type>\w+)"
        r"(?:\((?P<scope>[^\)]+)\))?"
        r"(?P<breaking>!)?"
        r":\s*"
        r"(?P<subject>.+?)$"
    )
    BREAKING_FOOTER_PATTERN = re.compile(
        r"^BREAKING[- ]CHANGE:\s*(.+)", re.MULTILINE
    )
    _FOOTER_LINE_PATTERNS: tuple[re.Pattern[str], ...] = (
        re.compile(r"^BREAKING[- ]CHANGE:"),
        re.compile(r"^[\w-]+:\s+"),
        re.compile(r"^[\w-]+\s+#\d+"),
    )

    def parse(self, message: str) -> CommitMessage:
        """Parse ``message`` into a :class:`CommitMessage`.

        Args:
            message: Raw commit message text. May be a single line or
                contain a body and footer separated by blank lines.

        Returns:
            A :class:`CommitMessage` populated with whichever fields
            could be extracted. Non-conventional messages return an
            empty-typed result with the original ``raw`` and ``header``.
        """
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
        breaking = match.group("breaking") is not None

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
            is_conventional=True,
        )

    def _extract_header(self, lines: list[str]) -> str:
        if not lines:
            return ""
        return lines[0].strip()

    def _extract_body(self, lines: list[str]) -> str:
        body, _ = self._split_body_footer(lines)
        return "\n".join(body).strip()

    def _extract_footer(self, lines: list[str]) -> str:
        _, footer = self._split_body_footer(lines)
        return "\n".join(footer).strip()

    def _split_body_footer(
        self, lines: list[str]
    ) -> tuple[list[str], list[str]]:
        # The Conventional Commits spec requires a blank-line separator
        # between body and footer. A `token: value` line buried in the body
        # is body content, not a footer — only a footer-token line that
        # follows a blank line marks the start of the footer block.
        if len(lines) <= 1:
            return [], []

        post_header = lines[1:]
        body_start = self._first_non_blank(post_header)
        if body_start is None:
            return [], []

        if self._is_footer_line(post_header[body_start]):
            return [], post_header[body_start:]

        footer_split = self._find_footer_split(post_header, body_start)
        if footer_split is not None:
            blank_idx, footer_idx = footer_split
            return (
                self._rstrip_blank(post_header[body_start:blank_idx]),
                post_header[footer_idx:],
            )

        return self._rstrip_blank(post_header[body_start:]), []

    @staticmethod
    def _first_non_blank(lines: list[str]) -> int | None:
        for i, line in enumerate(lines):
            if line.strip():
                return i
        return None

    def _find_footer_split(
        self, post_header: list[str], body_start: int
    ) -> tuple[int, int] | None:
        for i in range(body_start, len(post_header) - 1):
            if not post_header[i].strip() and self._is_footer_line(
                post_header[i + 1]
            ):
                return i, i + 1
        return None

    @staticmethod
    def _rstrip_blank(lines: list[str]) -> list[str]:
        result = list(lines)
        while result and not result[-1].strip():
            result.pop()
        return result

    def _is_footer_line(self, line: str) -> bool:
        return any(
            pattern.match(line) for pattern in self._FOOTER_LINE_PATTERNS
        )


class CommitParserFactory:
    """Constructs :class:`ConventionalCommitParser` instances."""

    @staticmethod
    def create() -> ConventionalCommitParser:
        """Return a default :class:`ConventionalCommitParser`."""
        return ConventionalCommitParser()
