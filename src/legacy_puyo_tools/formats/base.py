# SPDX-FileCopyrightText: 2021 Nick Woronekin
# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""A base class that defines what is required to convert and create a format."""

from __future__ import annotations

from abc import abstractmethod
from typing import BinaryIO, Protocol


class FormatError(Exception):
    """The data being decoded does not conform to the implemented format."""


class BaseFormat(Protocol):
    """A binary format with encoding and decoding support."""

    @classmethod
    @abstractmethod
    def decode(cls, fp: BinaryIO) -> BaseFormat:
        """Decode the implemented format from a file-like object.

        :param fp: A file-like object in binary mode containing data that follows the
            implemented format.

        :return: The object representation of the implemented format.
        """
        raise NotImplementedError

    @abstractmethod
    def encode(self, fp: BinaryIO) -> None:
        """Encode the implemented format to to a file-like object.

        :param fp: A file-like object in binary mode that the implemented will be
            encoded to.
        """
        raise NotImplementedError
