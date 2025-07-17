"""Fpd conversion tool for older Puyo games.

This module supports the encoding and decoding of the fpd format used by Puyo Puyo! 15th
Anniversary and Puyo Puyo 7.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

from codecs import BOM_UTF16_LE
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Self

from attrs import define

from legacy_puyo_tools.exceptions import FileFormatError, FormatError

ENCODING = "utf-16-le"
FPD_ENTRY_LENGTH = 3
UTF16_LENGTH = 2
WIDTH_ENTRY_OFFSET = 2


@define
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
    width: int

    def __init__(self, code_point: bytes, width: int = 0x00) -> None:
        """Initializes a fpd character.

        Args:
            code_point:
                A Unicode character in the UTF-16 LE format.
            width:
                The width of the character. Defaults to 0x00.
        """
        self.code_point = code_point.decode(ENCODING)
        self.width = width

    def encode(self) -> bytes:
        """Encodes the character back to a fpd character entry.

        Returns:
            The character in UTF-16 LE format and its width.
        """
        return self.code_point.encode(ENCODING) + self.width.to_bytes()

    @classmethod
    def decode(cls, fpd_entry: bytes) -> Self:
        """Decodes a fpd character into its code point and width.

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

        return cls(fpd_entry[:UTF16_LENGTH], fpd_entry[WIDTH_ENTRY_OFFSET])


@define
class Fpd:
    """A fpd character table.

    The fpd stores character table in which each entry is placed right next to each
    other and the indices is offset by multiples of `0x03`. I.e. The 1st character is at
    index `0x00`, the 2nd character is at index `0x03`, the 3rd character is at index
    `0x06`, etc.

    Attributes:
        entries:
            A list of fpd character entries.
    """

    entries: list[FpdCharacter]

    def __getitem__(self, index: int) -> str:
        """Retrieves a character from the fpd character table.

        Args:
            index:
                The index of the character to retrieve.

        Returns:
            A string that contains the requested character.
        """
        return self.entries[index].code_point

    @classmethod
    def read_fpd_from_path(cls, path: Path) -> Self:
        """Reads and extract characters from a fpd file.

        Args:
            path:
                A path to a fpd encoded file that contains a fpd character table.

        Raises:
            FileFormatError:
                The fpd file contain a entry that does not conform to the fpd character
                format.

        Returns:
            A fpd character table.
        """
        with Path(path).open("rb") as fp:
            try:
                return cls.read_fpd(fp)
            except FormatError as e:
                raise FileFormatError(f"{path} is not a valid fpd file") from e

    @classmethod
    def read_fpd(cls, fp: BinaryIO) -> Self:
        """Reads and extract characters from a file object.

        Args:
            fp:
                A file object that points to a fpd encoded stream.

        Returns:
            A fpd character table.
        """
        return cls.decode_fpd(fp.read())

    @classmethod
    def decode_fpd(cls, data: bytes) -> Self:
        """Extracts the fpd character table from a fpd encoded stream.

        Args:
            data:
                A fpd encoded stream that contains a fpd character table.

        Returns:
            A fpd character table.
        """
        return cls([
            FpdCharacter.decode(data[i : i + FPD_ENTRY_LENGTH])
            for i in range(0, len(data), FPD_ENTRY_LENGTH)
        ])

    def write_fpd_to_path(self, path: Path) -> None:
        """Writes the fpd character table to a fpd encoded file.

        Args:
            path:
                A path to write the fpd encoded stream.
        """
        with Path(path).open("wb") as fp:
            self.write_fpd(fp)

    def write_fpd(self, fp: BinaryIO) -> None:
        """Writes the fpd character table to a file object.

        Args:
            fp:
                A binary file object.
        """
        fp.write(self.encode_fpd())

    def encode_fpd(self) -> bytes:
        """Encodes the fpd character table into a fpd encoded stream.

        Returns:
            A fpd encoded stream that contains the fpd character table.
        """
        with BytesIO() as bytes_buffer:
            for character in self.entries:
                bytes_buffer.write(character.encode())

            return bytes_buffer.getvalue()

    @classmethod
    def read_unicode_from_path(cls, path: Path) -> Self:
        """Reads and convert characters from a UTF-16 little-endian text file.

        Arguments:
            path: A path to a UTF-16 LE text file.

        Raises:
            FileFormatError:
                The file is not a UTF-16 little-endian encoded text file or is missing
                the Byte Order Mark for UTF-16 little-endian.

        Returns:
            A fpd character table.
        """
        with Path(path).open("rb") as fp:
            # Check the Byte Order Mark (BOM) to see if it is really a UTF-16 LE text
            # file
            if fp.read(2) != BOM_UTF16_LE:
                raise FileFormatError(
                    f"{path} is not a UTF-16 little-endian text file."
                )

            return cls.read_unicode(fp)

    @classmethod
    def read_unicode(cls, fp: BinaryIO) -> Self:
        """Reads and convert UTF-16 LE characters from a file object.

        Args:
            fp:
                A binary file object.

        Returns:
            A fpd character table.
        """
        return cls.decode_unicode(fp.read())

    # TODO: Somehow allow people to specify the width of the character during decoding
    @classmethod
    def decode_unicode(cls, unicode: bytes) -> Self:
        """Converts a UTF-16 LE stream into a fpd character table.

        Args:
            unicode:
                A UTF-16 LE encoded character stream.

        Returns:
            A fpd character table.
        """
        return cls([
            FpdCharacter(unicode[i : i + UTF16_LENGTH])
            for i in range(0, len(unicode), UTF16_LENGTH)
        ])

    def write_unicode_to_path(self, path: Path) -> None:
        """Writes the fpd character table to a UTF-16 LE text file.

        Args:
            path:
                A path to store the converted UTF-16 LE text file.
        """
        with Path(path).open("wb") as fp:
            # Write the Byte Order Mark (BOM) for plain text editors
            fp.write(BOM_UTF16_LE)

            self.write_unicode(fp)

    def write_unicode(self, fp: BinaryIO) -> None:
        """Writes the fpd character table to a file object.

        Args:
            fp:
                A binary file object.
        """
        fp.write(self.encode_unicode())

    def encode_unicode(self) -> bytes:
        """Encodes the fpd character table into a UTF-16 LE text stream.

        Returns:
            A UTF-16 LE encoded text stream with characters from the fpd.
        """
        with BytesIO() as bytes_buffer:
            for character in self.entries:
                bytes_buffer.write(character.code_point.encode(ENCODING))

            return bytes_buffer.getvalue()
