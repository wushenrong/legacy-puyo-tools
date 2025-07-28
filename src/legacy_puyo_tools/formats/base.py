# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Base class that defines what is required to create a format."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import BinaryIO

# TODO: Remove typing extensions when migrating to Python 3.11.
from typing_extensions import Self

from legacy_puyo_tools.exceptions import FileFormatError, FormatError
from legacy_puyo_tools.formats._io import get_file_name, read_file
from legacy_puyo_tools.typing import StrPath


class Format(ABC):
    """Classes that implements a format and with encoding and decoding support."""

    @classmethod
    @abstractmethod
    def decode(cls, data: bytes) -> Self:
        """Decode byte streams into an object representation of the implemented format.

        :param data: A byte stream that contains data that follows the implemented
            format.

        :return: The object representation of the implemented format.
        """

    @classmethod
    def _decode_file(cls, path_or_buf: StrPath | BinaryIO, **kwargs: int) -> Self:
        """Decode a file that conforms to a format implemented by the class.

        :param path_or_buf: A string path, path-like object, or a file-like object that
            point to a file that contains data in the format that the class implements.

        :raises FileFormatError: The given file does not conform to the format that the
            class implements.

        :return: An object that represents the format that the class implements.
        """
        try:
            return cls.decode(read_file(path_or_buf), **kwargs)
        except FormatError as e:
            raise FileFormatError(
                f"{get_file_name(path_or_buf)} is not a valid {cls.__name__} file"
            ) from e

    @abstractmethod
    def encode(self) -> bytes:
        """Encode a format from an object into a byte stream.

        :return: A byte stream that conforms to the implemented format.
        """
