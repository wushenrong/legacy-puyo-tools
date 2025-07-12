from itertools import pairwise

from lxml import etree

from legacy_puyo_tools.fpd import Fpd

CHARACTER_WIDTH = 2
ENDIAN = "little"

INT32_OFFSET = 8
INT32_SIZE = 4
INT64_OFFSET = 16
INT64_SIZE = 8


def _read_character(data: bytes, i: int) -> int:
    return int.from_bytes(data[i : i + CHARACTER_WIDTH], ENDIAN)


def _create_offset_reader(width: int):
    def offset_reader(data: bytes, i: int):
        return int.from_bytes(data[i : i + width], ENDIAN)

    return offset_reader


def _calculate_integer_width(data: bytes):
    if int.from_bytes(data[:4], ENDIAN) == INT32_OFFSET:
        return (INT32_OFFSET, 4)

    if int.from_bytes(data[8:16], ENDIAN) == INT64_OFFSET:
        return (INT64_OFFSET, 8)

    raise NotImplementedError("")


type Mtx = list[list[int]]


def read_mtx(path: str) -> Mtx:
    with open(path, "rb") as fp:
        return from_mtx(fp.read())


def from_mtx(data: bytes) -> Mtx:
    if int.from_bytes(data[:4], ENDIAN) != len(data):
        raise NotImplementedError(
            "Remind the creator to create an exception for checking mtx length."
        )

    section_table_index_offset, int_width = _calculate_integer_width(data[4:16])
    read_offset = _create_offset_reader(int_width)

    section_table_offset = read_offset(data, section_table_index_offset)
    string_table_offset = read_offset(data, section_table_offset)

    sections = [
        read_offset(data, section_table_offset + (i * int_width))
        for i in range((string_table_offset - section_table_offset) // int_width)
    ]

    strings: list[list[int]] = []

    for current_string_offset, next_string_offset in pairwise(sections):
        string: list[int] = []

        for i in range(next_string_offset - current_string_offset):
            string.append(
                _read_character(data, current_string_offset + (i * CHARACTER_WIDTH))
            )

        strings.append(string)

    return strings


def write_xml(path: str, mtx: Mtx, fpd: Fpd):
    with open(path, "wb") as fp:
        fp.write(to_xml(mtx, fpd))


# TODO: Do something about the manual string formatting in tag
def to_xml(mtx: Mtx, fpd: Fpd) -> bytes:
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
        root, encoding="utf-8", xml_declaration=True, pretty_print=True
    )
