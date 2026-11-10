"""Errors and exit codes (S20).

0  every output was written or is unchanged
1  something failed; nothing was left half-written
2  finished, but some outputs were skipped (drift, or an existing file rosamta may not take over)
3  invalid configuration; nothing was written
"""

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_PARTIAL = 2
EXIT_CONFIG = 3


class RosamtaError(Exception):
    exit_code = EXIT_FAILED


class ConfigError(RosamtaError):
    """Invalid configuration. Nothing is written."""

    exit_code = EXIT_CONFIG
