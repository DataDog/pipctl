#!/usr/bin/env python3


class ExceptionBase(Exception):
    """A base class in exception hierarchy."""


class OSVError(ExceptionBase):
    """An exception raised when there is an error with OSV database."""


class ConfigError(ExceptionBase):
    """An error raised on any issue with configuration file."""


class ConfigNotFound(ConfigError):
    """An error raised when configuration file is not found."""


class ConfigParseError(ConfigError):
    """An error raised when configuration file cannot be parsed."""


class ConfigValidationError(ConfigError):
    """An error raised when configuration file fails to validate."""


class OSVDownloadError(OSVError):
    """An error raised when OSV database cannot be downloaded."""
