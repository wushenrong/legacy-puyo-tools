"""Base class that defines what is required to create a format.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from abc import ABC, abstractmethod

# TODO: Remove typing extensions when migrating to Python 3.11.
from typing_extensions import Self

from legacy_puyo_tools.formats._io import (
    FileFormatError,
    FormatError,
    PathOrFile,
    get_file_name,
    read_file,
)


class Format(ABC):
    """Classes that implements a format and with encoding and decoding support."""

    @classmethod
    @abstractmethod
    def decode(cls, data: bytes) -> Self:
        """Decode byte streams into an object representation of the implemented format.

        Arguments:
            data:
                A byte stream that contains data that follows the implemented format.

        Returns:
            The object representation of the implemented format.
        """

    @classmethod
    def _decode_file(cls, path_or_buf: PathOrFile, **kwargs: int) -> Self:
        """Decode a file that conforms to a format implemented by the class.

        Arguments:
            path_or_buf:
                A string path, path-like object, or a file-like object that point to a
                file that contains data in the format that the class implements.
            **kwargs:
                Any additional keywords arguments that the format needs for decoding.

        Raises:
            FileFormatError:
                The given file does not conform to the format that the class
                implements.

        Returns:
            An object that represents the format that the class implements.
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

        Returns:
            A byte stream that conforms to the implemented format.
        """
