"""Exceptions that might be thrown when parsing files.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""


class FormatError(Exception):
    """The current input data does not conform to an expected format."""


class FileFormatError(FormatError):
    """The file does not conform to a file format or is malformed."""


class ArgumentError(Exception):
    """One of the argument is invalid or missing."""
