from __future__ import annotations

import argparse
import pathlib
import sys
from codecs import BOM_UTF16_LE
from collections.abc import Callable
from typing import BinaryIO

from attrs import define

from legacy_puyo_tools.fpd import Fpd
from legacy_puyo_tools.mtx import Mtx


@define
class _CliNamespace(argparse.Namespace):
    func: Callable[[type[_CliNamespace]], None]
    file: BinaryIO
    output: BinaryIO
    unicode: BinaryIO
    fpd: BinaryIO
    version: bool


def _create_fpd(args: _CliNamespace) -> None:
    if args.file.read(2) != BOM_UTF16_LE:
        raise NotImplementedError()

    if args.output:
        Fpd.read_unicode(args.file).write_fpd(args.output)

        return

    path = pathlib.Path(args.file.name).with_suffix("")

    if path.suffix != ".fpd":
        path = path.with_suffix(".fpd")

    Fpd.read_unicode(args.file).write_fpd_to_path(path)


def _create_mtx(args: _CliNamespace) -> None:
    raise NotImplementedError()


def _convert_fpd(args: _CliNamespace) -> None:
    print(args)


def _convert_mtx(args: _CliNamespace) -> None:
    if args.fpd:
        fpd_data = Fpd.read_fpd(args.fpd)
    elif args.unicode:
        if args.unicode.read(2) != BOM_UTF16_LE:
            raise NotImplementedError()

        fpd_data = Fpd.read_fpd(args.unicode)
    else:
        raise NotImplementedError()

    if args.output:
        Mtx.read_mtx(args.file).write_xml(args.output, fpd_data)

        return

    path = pathlib.Path(args.file.name).with_suffix("")

    if path.suffix != ".xml":
        path = path.with_suffix(".xml")

    Mtx.read_mtx(args.file).write_xml_to_file(path, fpd_data)


def main() -> None:
    shared_options = argparse.ArgumentParser(add_help=False)
    shared_options.add_argument("file", type=argparse.FileType("rb"))
    shared_options.add_argument("-o", "--output", type=argparse.FileType("wb"))

    mtx_options = argparse.ArgumentParser(add_help=False, parents=[shared_options])
    mtx_options_group = mtx_options.add_mutually_exclusive_group(required=True)
    mtx_options_group.add_argument("--fpd", type=argparse.FileType("rb"))
    mtx_options_group.add_argument("--unicode", type=argparse.FileType("rb"))

    main_parser = argparse.ArgumentParser()
    main_parser.add_argument(
        "-v",
        "--version",
        help="show version",
        action="store_true",
    )

    sub_parser = main_parser.add_subparsers()

    create_parser = sub_parser.add_parser("create")
    create_sub_parser = create_parser.add_subparsers(required=True)

    create_fpd_parser = create_sub_parser.add_parser("fpd", parents=[shared_options])
    create_fpd_parser.set_defaults(func=_create_fpd)

    create_mtx_parser = create_sub_parser.add_parser("mtx", parents=[mtx_options])
    create_mtx_parser.set_defaults(func=_create_mtx)

    convert_parser = sub_parser.add_parser("convert")
    convert_sub_parser = convert_parser.add_subparsers(required=True)

    convert_fpd_parser = convert_sub_parser.add_parser("fpd", parents=[shared_options])
    convert_fpd_parser.set_defaults(func=_convert_fpd)

    convert_mtx_parser = convert_sub_parser.add_parser("mtx", parents=[mtx_options])
    convert_mtx_parser.set_defaults(func=_convert_mtx)

    args = main_parser.parse_args(namespace=_CliNamespace)

    if args.version:
        sys.exit()

    args.func(args)


if __name__ == "__main__":
    main()
