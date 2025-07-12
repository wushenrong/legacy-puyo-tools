import io
import pathlib
import typing
from codecs import BOM_UTF16_LE

ENCODING = "utf-16-le"
FPD_ENTRY_LENGTH = 3
UTF16_LENGTH = 2
# TODO: Better naming of this variable
WIDTH_ENTRY = 2


class FpdCharacter:
    def __init__(self, code_point: bytes, width: int = 0x00):
        self.code_point = code_point.decode(ENCODING)
        self.width = width

    def encode(self):
        return self.code_point.encode(ENCODING) + self.width.to_bytes()

    @classmethod
    def decode(cls, fpd_entry: bytes):
        if len(fpd_entry) % FPD_ENTRY_LENGTH != 0:
            raise NotImplementedError(
                "Remind the creator to create an exception for decoding character."
            )

        return cls(fpd_entry[:UTF16_LENGTH], fpd_entry[WIDTH_ENTRY])


class Fpd:
    def __init__(self, characters: list[FpdCharacter]):
        self.characters = characters

    @classmethod
    def read_fpd_from_file(cls, path: pathlib.Path):
        with open(path, "rb") as fp:
            return cls.read_fpd(fp)

    @classmethod
    def read_fpd(cls, fp: typing.BinaryIO):
        return cls.decode_fpd(fp.read())

    def write_fpd_to_file(self, path: pathlib.Path):
        with open(path, "wb") as fp:
            self.write_fpd(fp)

    def write_fpd(self, fp: typing.BinaryIO):
        fp.write(self.encode_fpd())

    @classmethod
    def decode_fpd(cls, data: bytes):
        return cls(
            [
                FpdCharacter.decode(data[i : i + FPD_ENTRY_LENGTH])
                for i in range(0, len(data), FPD_ENTRY_LENGTH)
            ]
        )

    def encode_fpd(self):
        with io.BytesIO() as bytes_buffer:
            for character in self.characters:
                bytes_buffer.write(character.encode())

            return bytes_buffer.getvalue()

    @classmethod
    def read_unicode_from_file(cls, path: pathlib.Path):
        with open(path, "rb") as fp:
            # Check the Byte Order Mark (BOM) to see if it is really a UTF-16-LE file
            if fp.read(2) != BOM_UTF16_LE:
                raise NotImplementedError(
                    "Remind the creator to create an exception for reading a file."
                )

            return cls.read_unicode(fp)

    @classmethod
    def read_unicode(cls, fp: typing.BinaryIO):
        return cls.decode_unicode(fp.read())

    def write_unicode_to_file(self, path: pathlib.Path):
        with open(path, "wb") as fp:
            # Write the Byte Order Mark (BOM) for plain text editors
            fp.write(BOM_UTF16_LE)

            self.write_unicode(fp)

    def write_unicode(self, fp: typing.BinaryIO):
        fp.write(self.encode_unicode())

    # TODO: Somehow allow people to specify the width of the character
    @classmethod
    def decode_unicode(cls, unicode: bytes):
        return cls(
            [
                FpdCharacter(unicode[i : i + UTF16_LENGTH])
                for i in range(0, len(unicode), UTF16_LENGTH)
            ]
        )

    def encode_unicode(self):
        with io.BytesIO() as bytes_buffer:
            for character in self.characters:
                bytes_buffer.write(character.code_point.encode(ENCODING))

            return bytes_buffer.getvalue()

    def get_code_point(self, index: int):
        return self.characters[index].code_point
