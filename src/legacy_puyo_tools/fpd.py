import os
import typing
from codecs import BOM_UTF16_LE
from dataclasses import dataclass

ENCODING = "utf-16-le"
CHARACTER_ENTRY_LENGTH = 3
CODE_POINT_WIDTH = 2
WIDTH_ENTRY = 2


@dataclass
class FpdCharacter:
    code_point: str
    width: int

    def __init__(self, code_point: bytes, width: int) -> None:
        self.code_point = code_point.decode(ENCODING)
        self.width = width


type FpdEntries = list[FpdCharacter]


def encode_fpd(fp: typing.BinaryIO, characters: FpdEntries) -> None:
    for character in characters:
        fp.write(character.code_point.encode(ENCODING) + character.width.to_bytes())


def decode_fpd(fp: typing.BinaryIO) -> FpdEntries:
    characters: FpdEntries = []

    while character := fp.read(CHARACTER_ENTRY_LENGTH):
        characters.append(
            FpdCharacter(character[:CODE_POINT_WIDTH], character[WIDTH_ENTRY])
        )

    return characters


def encode_unicode(fp: typing.BinaryIO, characters: FpdEntries) -> None:
    for entry in characters:
        fp.write(entry.code_point.encode(ENCODING))


def decode_unicode(fp: typing.BinaryIO) -> FpdEntries:
    characters: FpdEntries = []

    # TODO: Somehow allow people to specify the width of the character
    while character := fp.read(CODE_POINT_WIDTH):
        characters.append(FpdCharacter(character, 0x0D))

    return characters


def read_fpd_file(path: str) -> FpdEntries:
    if os.path.getsize(path) % CHARACTER_ENTRY_LENGTH != 0:
        raise NotImplementedError(
            "Remind the creator to create an exception for reading a fpd file."
        )

    with open(path, "rb") as fp:
        return decode_fpd(fp)


def write_fpd_file(path: str, characters: FpdEntries) -> None:
    with open(path, "wb") as fp:
        encode_fpd(fp, characters)


def read_unicode_file(path: str) -> FpdEntries:
    with open(path, "rb") as fp:
        bom = fp.read(2)

        if bom != BOM_UTF16_LE:
            raise NotImplementedError(
                "Remind the creator to create an exception for reading a unicode file."
            )

        return decode_unicode(fp)


def write_unicode_file(path: str, characters: FpdEntries) -> None:
    with open(path, "wb") as fp:
        # Write the Byte Order Mark for text editors
        fp.write(BOM_UTF16_LE)

        encode_unicode(fp, characters)
