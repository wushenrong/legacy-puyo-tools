# SPDX-FileCopyrightText: 2021 Nick Woronekin
# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Custom exceptions used by modules in legacy-puyo-tools."""


class DecompressionError(Exception):
    """There was a error during decompression."""

    def __init__(self, message: str, algorithm: str) -> None:
        """Creates a new DecompressionError exception."""
        self.message = message
        self.algorithm = algorithm
        super().__init__(message)


class FileFormatError(Exception):
    """The file being decoded does not conform to the implemented file format."""
