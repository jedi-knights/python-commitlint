"""Domain exceptions raised across the python-commitlint package."""


class ConfigurationError(Exception):
    """Raised when a commitlint configuration is malformed or invalid.

    Used at the configuration-loading boundary to surface a single,
    actionable error type instead of leaking ``ValueError`` / ``TypeError``
    / ``KeyError`` from internal parsing.
    """
