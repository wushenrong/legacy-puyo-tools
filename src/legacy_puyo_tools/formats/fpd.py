"""Fpd conversion tool for older Puyo games.

This module supports the encoding and decoding of the fpd format used by Puyo Puyo! 15th
Anniversary and Puyo Puyo 7.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from codecs import BOM_UTF16_LE
from io import BytesIO, StringIO

import attrs
from bidict import bidict

from legacy_puyo_tools.formats.base import FileFormatError, Format, FormatError
from legacy_puyo_tools.io import PathOrFile, get_file_handle, get_file_name

ENCODING = "utf-16-le"
FPD_ENTRY_LENGTH = 3
UTF16_LENGTH = 2
WIDTH_ENTRY_OFFSET = 2


@attrs.frozen
class FpdCharacter:
    """A fpd character entry.

    A fpd character is a binary entry that is 3 bytes long and formatted as follows:
    `XX XX YY`. Where `XX XX` is the character encoded in UTF-16 little-endian and `YY`
    is the width of the character.

    Attributes:
        code_point:
            A string that stores a single character.
        width:
            How wide should the character be, only used in the Nintendo DS versions of
            the games.
    """

    code_point: str
    width: int = attrs.field(default=0x00, eq=False)

    def __str__(self) -> str:
        """Return the character as a single character string."""
        return self.code_point

    @classmethod
    def decode(cls, fpd_entry: bytes) -> FpdCharacter:
        """Decode a fpd character into its code point and width.

        Args:
            fpd_entry:
                A fpd character entry that is 3 bytes long.

        Raises:
            FormatError:
                The entry given does not conform to the fpd character format.

        Returns:
            A fpd character entry containing its code point and width.
        """
        if len(fpd_entry) != FPD_ENTRY_LENGTH:
            raise FormatError(f"{fpd_entry} does not matches size {FPD_ENTRY_LENGTH}")

        code_point = fpd_entry[:UTF16_LENGTH].decode(ENCODING)
        width = fpd_entry[WIDTH_ENTRY_OFFSET]

        return cls(code_point, width)

    def encode(self) -> bytes:
        """Encode the character back to a fpd character entry.

        Returns:
            The character in UTF-16 LE format and its width.
        """
        # TODO: When updating Python to 3.11, remove arguments from width.to_bytes
        return self.code_point.encode(ENCODING) + self.width.to_bytes(1, "little")


@attrs.define
class Fpd(Format):
    """A fpd character table.

    The fpd stores character table in which each entry is placed right next to each
    other and the indices is offset by multiples of `0x03`. I.e. The 1st character is at
    index `0x00`, the 2nd character is at index `0x03`, the 3rd character is at index
    `0x06`, etc.

    Attributes:
        entries:
            A bidirectional dictionary of fpd character entries.
    """

    entries: bidict[int, FpdCharacter]

    def __getitem__(self, index: int) -> str:
        """Retrieve a character from the fpd character table.

        Args:
            index:
                The index of a character in the fpd character table..

        Returns:
            A string that contains the requested character.
        """
        return str(self.entries[index])

    def __str__(self) -> str:
        """Return a string representation of the fpd character table."""
        with StringIO() as string_buffer:
            for character in self.entries.inverse:
                string_buffer.write(str(character))

            return string_buffer.getvalue()

    def get_index(self, character: str) -> int:
        """Get the index of a character from the fpd character table.

        Args:
            character:
                A character that is in the fpd character table.

        Returns:
            A index of the character in the fpd character table.
        """
        return self.entries.inverse[FpdCharacter(character)]

    @classmethod
    def read_fpd(cls, path_or_buf: PathOrFile) -> Fpd:
        """Read and extract characters from a fpd file.

        Args:
            path_or_buf:
                A path or file-like object to a fpd encoded file that contains a fpd
                character table.

        Returns:
            A fpd character table.
        """
        return super()._decode_file(path_or_buf)

    @classmethod
    def decode(cls, data: bytes) -> Fpd:
        """Extract the fpd character table from a fpd encoded stream.

        Args:
            data:
                A fpd encoded stream that contains a fpd character table.

        Returns:
            A fpd character table.
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

        Returns:
            A fpd encoded stream that contains the fpd character table.
        """
        with BytesIO() as bytes_buffer:
            for character in self.entries.inverse:
                bytes_buffer.write(character.encode())

            return bytes_buffer.getvalue()

    def write_fpd(self, path_or_buf: PathOrFile) -> None:
        """Write the fpd character table to a fpd encoded file.

        Args:
            path_or_buf:
                A path or file-like object to write the fpd encoded stream.
        """
        with get_file_handle(path_or_buf, "wb") as fp:
            fp.write(self.encode())

    @classmethod
    def read_unicode(cls, path_or_buf: PathOrFile) -> Fpd:
        """Read and convert characters from a UTF-16 little-endian text file.

        Arguments:
            path_or_buf: A path or file-like object to a UTF-16 LE text file.

        Raises:
            FileFormatError:
                The file is not a UTF-16 little-endian encoded text file or is missing
                the Byte Order Mark for UTF-16 little-endian.

        Returns:
            A fpd character table.
        """
        with get_file_handle(path_or_buf) as fp:
            # Check the Byte Order Mark (BOM) to see if it is really a UTF-16 LE text
            # file
            if fp.read(2) != BOM_UTF16_LE:
                raise FileFormatError(
                    f"{get_file_name(path_or_buf)} is not a UTF-16 little-endian file"
                )

            return cls.from_unicode(fp.read())

    # TODO: Get width from another file
    @classmethod
    def from_unicode(cls, unicode: bytes, *, width: int = 0x0) -> Fpd:
        """Convert a UTF-16 LE stream into a fpd character table.

        Args:
            unicode:
                A UTF-16 LE encoded character stream.
            width:
                How wide is the character graphic in the fmp.

        Returns:
            A fpd character table.
        """
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

        Returns:
            A UTF-16 LE encoded text stream with characters from the fpd.
        """
        return str(self).encode(ENCODING)

    def write_unicode(self, path_or_buf: PathOrFile) -> None:
        """Write the fpd character table to a UTF-16 LE text file.

        Args:
            path_or_buf:
                A path or file-like object to store the converted UTF-16 LE text file.
        """
        with get_file_handle(path_or_buf, "wb") as fp:
            # Write the Byte Order Mark (BOM) for plain text editors
            fp.write(BOM_UTF16_LE)
            fp.write(self.to_unicode())
