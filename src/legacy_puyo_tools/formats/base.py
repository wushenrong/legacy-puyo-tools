"""Base class that defines what is required to create a format.

SPDX-FileCopyrightText: 2021 Nick Woronekin
SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from typing_extensions import Self

from legacy_puyo_tools.io import PathOrFile, get_file_handle, get_file_name


class FormatError(Exception):
    """The current input data does not conform to an expected format."""


class FileFormatError(FormatError):
    """The file does not conform to a file format or is malformed."""


class Format(ABC):
    """Classes that implements a format and with encoding and decoding support."""

    @classmethod
    @abstractmethod
    def decode(cls, data: bytes) -> Self:
        """Decode byte streams into an object representation of the implemented format.

        Args:
            data:
                A byte stream that contains data that follows the implemented format.
            **kwargs:
                Any additional keywords arguments that the format need for decoding.

        Returns:
            The object representation of the implemented format.
        """

    @classmethod
    def _decode_file(cls, path_or_buf: PathOrFile, **kwargs: int | None) -> Self:
        """Decode file that conforms to a format into an object.

        Args:
            cls:
                A class that implements a format.
            path_or_buf:
                A string path, path-like object, or a file-like object that point to a
                file that contains data in the format that the class implements.
            **kwargs:
                Any additional keywords arguments that the format need for decoding.

        Raises:
            FileFormatError:
                The given file does not conform to the format that the class
                implements.

        Returns:
            An object that represents the format that the class implements.
        """
        with get_file_handle(path_or_buf) as fp:
            try:
                return cls.decode(fp.read(), **kwargs)
            except FormatError as e:
                raise FileFormatError(
                    f"{get_file_name(path_or_buf)} is not a valid {cls.__name__} file"
                ) from e

    @abstractmethod
    def encode(self) -> bytes:
        """Encode a format from a Python object into a byte stream.

        Returns:
            A byte stream that conforms to the implemented format.
        """
