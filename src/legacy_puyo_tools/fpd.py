"""`fpd` conversion tool for Puyo Puyo! 15th Anniversary and Puyo Puyo 7.

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
    def __init__(self, code_point: bytes, width: int = 0x00) -> None:
        self.code_point: str = code_point.decode(ENCODING)
        self.width: int = width

    def encode(self) -> bytes:
        return self.code_point.encode(ENCODING) + self.width.to_bytes()

    @classmethod
    def decode(cls, fpd_entry: bytes) -> Self:
        if len(fpd_entry) != FPD_ENTRY_LENGTH:
            raise FormatError(f"{fpd_entry} does not matches size {FPD_ENTRY_LENGTH}")

        return cls(fpd_entry[:UTF16_LENGTH], fpd_entry[WIDTH_ENTRY_OFFSET])


@define
class Fpd:
    entry: list[FpdCharacter]

    def __getitem__(self, index: int) -> str:
        """Gets the actual character inside a fpd at a given index.

        Args:
            index (int): The index of the character in the fpd

        Returns:
            str: _description_
        """
        return self.entry[index].code_point

    @classmethod
    def read_fpd_from_path(cls, path: Path) -> Self:
        with Path(path).open("rb") as fp:
            try:
                return cls.read_fpd(fp)
            except FormatError as e:
                raise FileFormatError(f"{path} is not a valid fpd file") from e

    @classmethod
    def read_fpd(cls, fp: BinaryIO) -> Self:
        return cls.decode_fpd(fp.read())

    def write_fpd_to_path(self, path: Path) -> None:
        with Path(path).open("wb") as fp:
            self.write_fpd(fp)

    def write_fpd(self, fp: BinaryIO) -> None:
        fp.write(self.encode_fpd())

    @classmethod
    def decode_fpd(cls, data: bytes) -> Self:
        return cls(
            [
                FpdCharacter.decode(data[i : i + FPD_ENTRY_LENGTH])
                for i in range(0, len(data), FPD_ENTRY_LENGTH)
            ],
        )

    def encode_fpd(self) -> bytes:
        with BytesIO() as bytes_buffer:
            for character in self.entry:
                bytes_buffer.write(character.encode())

            return bytes_buffer.getvalue()

    @classmethod
    def read_unicode_from_path(cls, path: Path) -> Self:
        with Path(path).open("rb") as fp:
            # Check the Byte Order Mark (BOM) to see if it is really a UTF-16 LE encoded
            # text file
            if fp.read(2) != BOM_UTF16_LE:
                raise FileFormatError(
                    f"{path} is not a UTF-16 little-endian encoded text file.",
                )

            return cls.read_unicode(fp)

    @classmethod
    def read_unicode(cls, fp: BinaryIO) -> Self:
        return cls.decode_unicode(fp.read())

    def write_unicode_to_path(self, path: Path) -> None:
        with Path(path).open("wb") as fp:
            # Write the Byte Order Mark (BOM) for plain text editors
            fp.write(BOM_UTF16_LE)

            self.write_unicode(fp)

    def write_unicode(self, fp: BinaryIO) -> None:
        fp.write(self.encode_unicode())

    # TODO: Somehow allow people to specify the width of the character during decoding
    @classmethod
    def decode_unicode(cls, unicode: bytes) -> Self:
        return cls(
            [
                FpdCharacter(unicode[i : i + UTF16_LENGTH])
                for i in range(0, len(unicode), UTF16_LENGTH)
            ],
        )

    def encode_unicode(self) -> bytes:
        with BytesIO() as bytes_buffer:
            for character in self.entry:
                bytes_buffer.write(character.code_point.encode(ENCODING))

            return bytes_buffer.getvalue()
