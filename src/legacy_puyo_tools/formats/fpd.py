# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Fpd conversion tool for older Puyo games.

This module supports the encoding and decoding of the fpd format used by Puyo Puyo! 15th
Anniversary and Puyo Puyo 7.
"""

from __future__ import annotations

from io import BytesIO, StringIO
from typing import BinaryIO

import attrs
from bidict import bidict

from legacy_puyo_tools.formats._io import (
    UTF16_LENGTH,
    read_unicode_file,
    write_file,
    write_unicode_file,
)
from legacy_puyo_tools.formats.base import Format, FormatError
from legacy_puyo_tools.typing import StrPath

FPD_ENCODING = "utf-16-le"
"""The default character encoding that the fpd character table uses."""
FPD_ENTRY_LENGTH = 3
"""The length of a fpd character entry."""
FPD_WIDTH_OFFSET = 2
"""The offset of the width in a fpd character entry."""


@attrs.frozen
class FpdCharacter:
    """A fpd character entry.

    A fpd character is a binary entry that is 3 bytes long and formatted as follows:
    `XX XX YY`. Where `XX XX` is the character encoded in UTF-16 little-endian and `YY`
    is the width of the character.
    """

    code_point: str
    """A string that stores a single character."""
    width: int = attrs.field(default=0x00, eq=False)
    """How wide should the character be, only used in the Nintendo DS versions of the
    games."""

    def __str__(self) -> str:
        """Return the character as a single character string."""
        return self.code_point

    @classmethod
    def decode(cls, fpd_entry: bytes) -> FpdCharacter:
        """Decode a fpd character into its code point and width.

        :param fpd_entry: A fpd character entry that is 3 bytes long.

        :raises FormatError: The entry given does not conform to the fpd character
            format.

        :return: A fpd character entry containing its code point and width.
        """
        if len(fpd_entry) != FPD_ENTRY_LENGTH:
            raise FormatError(f"{fpd_entry} does not matches size {FPD_ENTRY_LENGTH}")

        code_point = fpd_entry[: FPD_ENTRY_LENGTH - 1].decode(FPD_ENCODING)
        width = fpd_entry[FPD_WIDTH_OFFSET]

        return cls(code_point, width)

    def encode(self) -> bytes:
        """Encode the character back to a fpd character entry.

        :return: The character in UTF-16 LE format and its width.
        """
        # TODO: When updating Python to 3.11, remove for to_bytes
        return self.code_point.encode(FPD_ENCODING) + self.width.to_bytes(1, "little")


@attrs.define
class Fpd(Format):
    """A fpd character table.

    The fpd stores a character table in which each entry is placed right next to each
    other and the indices is offset by multiples of `0x03`. I.e. The 1st character is at
    index `0x00`, the 2nd character is at index `0x03`, the 3rd character is at index
    `0x06`, etc.
    """

    entries: bidict[int, FpdCharacter]
    """A bidirectional dictionary of fpd character entries."""

    def __getitem__(self, index: int) -> str:
        """Return a character from the fpd character table."""
        return str(self.entries[index])

    def __str__(self) -> str:
        """Return a string representation of the fpd character table."""
        with StringIO() as string_buffer:
            for character in self.entries.inverse:
                string_buffer.write(str(character))

            return string_buffer.getvalue()

    def get_index(self, character: str) -> int:
        """Return the index of a character from the fpd character table."""
        return self.entries.inverse[FpdCharacter(character)]

    @classmethod
    def read_fpd(cls, path_or_buf: StrPath | BinaryIO) -> Fpd:
        """Read and decode the fpd character table from a fpd file.

        :param path_or_buf: A string path or file-like object in binary mode to
            a fpd encoded file that contains a fpd character table.

        :return: A fpd character table.
        """
        return super()._decode_file(path_or_buf)

    @classmethod
    def decode(cls, data: bytes) -> Fpd:
        """Decode the fpd character table from a fpd encoded stream.

        :param data: A fpd encoded stream that contains a fpd character table.

        :return: A fpd character table.
        """
        return cls(
            bidict({
                i // FPD_ENTRY_LENGTH: FpdCharacter.decode(
                    data[i : i + FPD_ENTRY_LENGTH]
                )
                for i in range(0, len(data), FPD_ENTRY_LENGTH)
            })
        )

    def encode(self) -> bytes:
        """Encode the fpd character table into a fpd encoded stream.

        :return: A fpd character table encoded into a byte stream.
        """
        with BytesIO() as bytes_buffer:
            for character in self.entries.inverse:
                bytes_buffer.write(character.encode())

            return bytes_buffer.getvalue()

    def write_fpd(self, path_or_buf: StrPath | BinaryIO) -> None:
        """Write the fpd character table to a fpd encoded file.

        :param path_or_buf: A string path or file-like object in binary mode to write
            the fpd character table.
        """
        write_file(path_or_buf, self.encode())

    @classmethod
    def read_unicode(cls, path_or_buf: StrPath | BinaryIO) -> Fpd:
        """Read and decode characters from a UTF-16 little-endian text file.

        :param path_or_buf: A string path or file-like object to a UTF-16 LE text file.

        :return: A fpd character table.
        """
        return cls.from_unicode(read_unicode_file(path_or_buf))

    # TODO: Find a way to get the width from another file
    @classmethod
    def from_unicode(cls, unicode: bytes, *, width: int = 0x0) -> Fpd:
        """Decode a UTF-16 LE stream into a fpd character table.

        :param unicode: A UTF-16 LE encoded character stream.
        :param width: How wide is the character graphic in the fmp.

        :return: A fpd character table.
        """
        # TODO: When updating Python to 3.11, remove for to_bytes
        return cls(
            bidict({
                i // UTF16_LENGTH: FpdCharacter.decode(
                    unicode[i : i + UTF16_LENGTH] + width.to_bytes(1, "little")
                )
                for i in range(0, len(unicode), UTF16_LENGTH)
            })
        )

    def to_unicode(self) -> bytes:
        """Encode the fpd character table into a UTF-16 LE text stream.

        :return: A UTF-16 LE encoded text stream with characters from the fpd.
        """
        return str(self).encode(FPD_ENCODING)

    def write_unicode(self, path_or_buf: StrPath | BinaryIO) -> None:
        """Write the fpd character table to a UTF-16 LE text file.

        :param path_or_buf: A string path or file-like object in binary mode to store
            the encoded UTF-16 LE text file.
        """
        write_unicode_file(path_or_buf, self.to_unicode())
