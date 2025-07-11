import io
from codecs import BOM_UTF16_LE

ENCODING = "utf-16-le"
FPD_ENTRY_LENGTH = 3
UTF16_LENGTH = 2
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


type Fpd = list[FpdCharacter]


def read_fpd(path: str) -> Fpd:
    with open(path, "rb") as fp:
        return decode_fpd(fp.read())


def decode_fpd(data: bytes) -> Fpd:
    return [
        FpdCharacter.decode(data[i : i + FPD_ENTRY_LENGTH])
        for i in range(0, len(data), FPD_ENTRY_LENGTH)
    ]


def write_fpd(path: str, fpd: Fpd):
    with open(path, "wb") as fp:
        fp.write(encode_fpd(fpd))


def encode_fpd(fpd: Fpd):
    with io.BytesIO() as bytes_buffer:
        for character in fpd:
            bytes_buffer.write(character.encode())

        return bytes_buffer.getvalue()


def read_unicode_file(path: str):
    with open(path, "rb") as fp:
        # Check the Byte Order Mark (BOM) to see if it is really a UTF-16-LE file
        if fp.read(2) != BOM_UTF16_LE:
            raise NotImplementedError(
                "Remind the creator to create an exception for reading a file."
            )

        return from_unicode(fp.read())


# TODO: Somehow allow people to specify the width of the character
def from_unicode(unicode: bytes):
    return [
        FpdCharacter(unicode[i : i + UTF16_LENGTH])
        for i in range(0, len(unicode), UTF16_LENGTH)
    ]


def write_unicode_file(path: str, fpd: Fpd) -> None:
    with open(path, "wb") as fp:
        # Write the Byte Order Mark (BOM) for plain text editors
        fp.write(BOM_UTF16_LE + to_unicode(fpd))


def to_unicode(fpd: Fpd):
    with io.BytesIO() as bytes_buffer:
        for character in fpd:
            bytes_buffer.write(character.code_point.encode(ENCODING))

        return bytes_buffer.getvalue()
