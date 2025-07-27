# SPDX-FileCopyrightText: 2021 Nick Woronekin
# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Exceptions that might be thrown when parsing files for converters."""


class FormatError(Exception):
    """The current input data does not conform to an expected format."""


class FileFormatError(FormatError):
    """The file does not conform to a file format or is malformed."""
