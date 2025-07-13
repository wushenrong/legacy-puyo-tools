"""Exceptions that might be thrown when parsing files.

SPDX-FileCopyrightText: 2025 Samuel Wu

SPDX-License-Identifier: MIT
"""


class FormatError(Exception):
    """Raised when the current input data does not conform to an expected format."""


class FileFormatError(FormatError):
    """Raised when a file does not conform to a file format or is malformed."""
