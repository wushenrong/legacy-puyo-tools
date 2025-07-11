import typing
from itertools import pairwise

from lxml import etree

from legacy_puyo_tools.fpd import FpdEntries

MTX_VER_1 = 8

SIZE_WIDTH = 2
CHARACTER_WIDTH = 2
INT_WIDTH = 4
ENDIAN = "little"

type MtxEntries = list[list[int]]


def bytes_to_int_le(data: bytes) -> int:
    return int.from_bytes(data, ENDIAN)


def read_int16_le(fp: typing.BinaryIO) -> int:
    return bytes_to_int_le(fp.read(2))


def read_int32_le(fp: typing.BinaryIO) -> int:
    return bytes_to_int_le(fp.read(INT_WIDTH))


def decode_mtx(fp: typing.BinaryIO) -> MtxEntries:
    mtx_length = read_int32_le(fp)

    if read_int32_le(fp) != MTX_VER_1:
        raise NotImplementedError(
            "Remind the creator to create an exception to check the version of mtx."
        )

    section_table_offset = read_int32_le(fp)
    text_table_offset = read_int32_le(fp)

    sections = [text_table_offset]

    while fp.tell() < text_table_offset:
        sections.append(read_int32_le(fp))

    if len(sections) != (text_table_offset - section_table_offset) / INT_WIDTH:
        raise NotImplementedError(
            "Remind the creator to create an exception for checking sections in mtx."
        )

    string_lengths: list[int] = []

    for current_string_offset, next_string_offset in pairwise(sections):
        string_lengths.append(next_string_offset - current_string_offset)

    strings: MtxEntries = []

    for string_offset, string_length in zip(sections, string_lengths):
        string: list[int] = []

        while fp.tell() < string_offset + string_length:
            string.append(read_int16_le(fp))

        strings.append(string)

    leftover_data = fp.read()

    if fp.tell() != mtx_length:
        raise NotImplementedError(
            "Remind the creator to create an exception for checking mtx length."
        )

    strings.append(
        [
            bytes_to_int_le(leftover_data[i : i + CHARACTER_WIDTH])
            for i in range(0, len(leftover_data), CHARACTER_WIDTH)
        ]
    )

    return strings


def encode_xml(mtx: MtxEntries, fpd: FpdEntries) -> bytes:
    root = etree.Element("mtx")
    sheet = etree.SubElement(root, "sheet")

    for string in mtx:
        dialog = etree.SubElement(sheet, "text")
        dialog.text = "\n"

        for character in string:
            match character:
                case 0xF813:
                    dialog.append(etree.Element("arrow"))
                case 0xFFFD:
                    dialog.text += "\n"
                case 0xFFFF:
                    break
                case _:
                    dialog.text += fpd[character].code_point

    etree.indent(root)

    return etree.tostring(
        root, encoding="utf-8", pretty_print=True, xml_declaration=True
    )


def read_mtx_file(path: str) -> MtxEntries:
    with open(path, "rb") as fp:
        return decode_mtx(fp)
