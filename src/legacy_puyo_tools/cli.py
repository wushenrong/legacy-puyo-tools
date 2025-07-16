"""A commandline application that interfaces with conversion tools.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import sys
from argparse import ArgumentParser
from codecs import BOM_UTF16_LE
from collections.abc import Callable
from importlib import metadata
from pathlib import Path
from typing import BinaryIO

from attrs import define

from legacy_puyo_tools.exceptions import FileFormatError
from legacy_puyo_tools.fpd import Fpd
from legacy_puyo_tools.mtx import Mtx


# We disable slots because the func attribute is not callable when it is
# enabled.
@define(slots=False)
class _CliNamespace(argparse.Namespace):
    func: Callable[[type[_CliNamespace]], None]
    input: BinaryIO
    output: BinaryIO
    unicode: BinaryIO
    fpd: BinaryIO
    subcommand: str
    version: bool


def _create_fpd(args: _CliNamespace) -> None:
    if args.input.read(2) != BOM_UTF16_LE:
        raise FileFormatError(
            f"{args.input.name} is not a UTF-16 little-endian encoded text"
            "file."
        )

    if args.output:
        Fpd.read_unicode(args.input).write_fpd(args.output)
        return

    path = Path(args.input.name).with_suffix("")

    if path.suffix != ".fpd":
        path = path.with_suffix(".fpd")

    Fpd.read_unicode(args.input).write_fpd_to_path(path)


def _create_mtx(args: _CliNamespace) -> None:
    raise NotImplementedError()


def _convert_fpd(args: _CliNamespace) -> None:
    if args.output:
        args.output.write(BOM_UTF16_LE)
        Fpd.read_fpd(args.input).write_fpd(args.output)
        return

    path = Path(args.input.name).with_suffix("")

    if path.suffix != ".fpd":
        path = path.with_suffix(".fpd")

    Fpd.read_fpd(args.input).write_unicode_to_path(path)


def _convert_mtx(args: _CliNamespace) -> None:
    if args.fpd:
        fpd_data = Fpd.read_fpd(args.fpd)
    else:
        if args.unicode.read(2) != BOM_UTF16_LE:
            raise FileFormatError(
                f"{args.input.name} is not a UTF-16 little-endian encoded text"
                "file."
            )

        fpd_data = Fpd.read_unicode(args.unicode)

    if args.output:
        Mtx.read_mtx(args.input).write_xml(args.output, fpd_data)
        return

    path = Path(args.input.name).with_suffix("")

    if path.suffix != ".xml":
        path = path.with_suffix(".xml")

    Mtx.read_mtx(args.input).write_xml_to_file(path, fpd_data)


def _add_create_parsers(
    create_parser: ArgumentParser,
    shared_options: ArgumentParser,
    mtx_options: ArgumentParser,
) -> None:
    create_sub_parsers = create_parser.add_subparsers()

    create_fpd_parser = create_sub_parsers.add_parser(
        "fpd",
        help="create a fpd file from a unicode text file",
        parents=[shared_options],
    )
    create_fpd_parser.set_defaults(func=_create_fpd)

    create_mtx_parser = create_sub_parsers.add_parser(
        "mtx", help="create a mtx file from a XML file", parents=[mtx_options]
    )
    create_mtx_parser.set_defaults(func=_create_mtx)


def _add_convert_parsers(
    convert_parser: ArgumentParser,
    shared_options: ArgumentParser,
    mtx_options: ArgumentParser,
) -> None:
    convert_sub_parsers = convert_parser.add_subparsers()

    convert_fpd_parser = convert_sub_parsers.add_parser(
        "fpd",
        help="convert a fpd file to a unicode file",
        parents=[shared_options],
    )
    convert_fpd_parser.set_defaults(func=_convert_fpd)

    convert_mtx_parser = convert_sub_parsers.add_parser(
        "mtx", help="convert a mtx file to XML file", parents=[mtx_options]
    )
    convert_mtx_parser.set_defaults(func=_convert_mtx)


def _add_sub_parsers(main_parser: ArgumentParser) -> dict[str, ArgumentParser]:
    shared_options = ArgumentParser(add_help=False)
    shared_options.add_argument(
        "input", type=argparse.FileType("rb"), help="input file"
    )
    shared_options.add_argument(
        "-o", "--output", type=argparse.FileType("wb"), help="output file"
    )

    mtx_options = ArgumentParser(add_help=False, parents=[shared_options])
    mtx_options_group = mtx_options.add_mutually_exclusive_group(required=True)
    mtx_options_group.add_argument(
        "--fpd", type=argparse.FileType("rb"), help="fpd file"
    )
    mtx_options_group.add_argument(
        "--unicode", type=argparse.FileType("rb"), help="unicode text file"
    )

    sub_parsers = main_parser.add_subparsers(
        title="subcommands", dest="subcommand"
    )

    subcommand_parsers = {
        "create_parser": sub_parsers.add_parser(
            "create", help="Create files that are used by older Puyo games"
        ),
        "convert_parser": sub_parsers.add_parser(
            "convert",
            help="Convert files used by older Puyo games to a readable format",
        ),
    }

    _add_create_parsers(
        subcommand_parsers["create_parser"], shared_options, mtx_options
    )
    _add_convert_parsers(
        subcommand_parsers["convert_parser"], shared_options, mtx_options
    )

    return subcommand_parsers


def main() -> None:
    """Entry point for the commandline application."""
    main_parser = ArgumentParser(
        description="A conversion tool for files used by older Puyo games."
    )
    main_parser.add_argument(
        "-v", "--version", help="show version", action="store_true"
    )

    subcommand_parsers = _add_sub_parsers(main_parser)

    args = main_parser.parse_args(namespace=_CliNamespace)

    if args.version is True:
        package_name = "legacy-puyo-tools"
        version = metadata.version(package_name)

        print(f"{package_name} {version}")

        sys.exit(0)

    if not hasattr(args, "func"):
        if args.subcommand == "create":
            subcommand_parsers["create_parser"].print_help(sys.stderr)
        elif args.subcommand == "convert":
            subcommand_parsers["convert_parser"].print_help(sys.stderr)
        else:
            main_parser.print_help(sys.stderr)

        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
