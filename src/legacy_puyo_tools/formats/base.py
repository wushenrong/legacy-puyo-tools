# SPDX-FileCopyrightText: 2021 Nick Woronekin
# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""A base class that defines what is required to convert and create a format."""

from __future__ import annotations

from abc import abstractmethod
from typing import BinaryIO, Protocol


class BaseFileFormat(Protocol):
    """A binary file format with encoding and decoding support."""

    @classmethod
    @abstractmethod
    def decode(cls, fp: BinaryIO) -> BaseFileFormat:
        """Decode the implemented file format from a file-like object.

        Arguments:
            fp: A file-like object in binary mode containing data that follows the
                implemented file format.

        Returns:
            The object representation of the implemented file format.
        """
        raise NotImplementedError

    @abstractmethod
    def encode(self, fp: BinaryIO) -> None:
        """Encode the implemented file format to to a file-like object.

        Arguments:
            fp:
                A file-like object in binary mode that the implemented file
                format will be encoded to.
        """
        raise NotImplementedError


class BaseCharacterTable(Protocol):
    """A file format that implements character table."""

    @abstractmethod
    def __getitem__(self, index: int) -> str:
        """Return a character from the character table by index."""
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        """Return all of the characters in the character table as a string."""
        raise NotImplementedError
