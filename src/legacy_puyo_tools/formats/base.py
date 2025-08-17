# SPDX-FileCopyrightText: 2021 Nick Woronekin
# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""A base class that defines what is required to convert and create a format."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import BinaryIO

# TODO: Remove typing extensions when migrating to Python 3.11.
from typing_extensions import Self


class FormatError(Exception):
    """The data being decoded does not conform to the implemented format."""


class BaseFormat(ABC):
    """A binary format with encoding and decoding support."""

    @classmethod
    @abstractmethod
    def decode(cls, fp: BinaryIO) -> Self:
        """Decode the implemented format from a file-like object.

        :param fp: A file-like object in binary mode containing data that follows the
            implemented format.

        :return: The object representation of the implemented format.
        """

    @abstractmethod
    def encode(self, fp: BinaryIO) -> None:
        """Encode the implemented format to to a file-like object.

        :param fp: A file-like object in binary mode that the implemented will be
            encoded to.
        """
