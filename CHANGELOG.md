# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Calendar Versioning](https://calver.org/) as of
July 23, 2025 (2025-07-23) where each number is the year, month, and day
respectively.

This project is still in development, expect **major breaking changes** over its
lifetime.

## Unreleased

### Added

- Support for 64 bit offsets for `mtx`.

### Changed

- Internal functions to raise exceptions if our expectations are somehow wrong.

### Removed

- Unneeded arguments that is leftover from Python 3.11.

## 2025-10-10

### Added

- Option to orient the `fmp` character graphics table in portrait or landscape.
- Exceptions when Unicode characters is unable to encode to `fpd`.
- Support for 3.14.

### Changed

- Use a CSV file instead of a Unicode text file for a human editable file format.
- Rewrite decoders to take in file-like objects instead of the entire file.
- Moved types back into formats instead being in a typing module.
- Convert non-black and white images instead of raising an exception.
- Use PNG as the default image format instead of BMP.
- Split the cli into create and convert commands.

### Removed

- Methods that take in string paths to read and write files.
- Option to specify the maximum width for `fmp` character graphics table.
- Support for Python 3.10 and 3.11.
- The ability to run the tools using runpy or `python -m`.

## 2025.8.2

### Changed

- Moved sample data for tests into their own files.
- Using an ordered bidirectional dictionary for `fpd`.
- Allow duplicate entries in the `fpd` by mapping indexes to indexes.

## 2025.7.30

### Changed

- `typing_extensions` to be a runtime dependency.

## 2025.7.29

### Added

- Documentation site at <https://wushenrong.github.io/legacy-puyo-tools/>.

### Changed

- Restructure project again for better documentation.
- The code of conduct to 3.0 of the Contributor Covenant.
- Contributing guidelines for this project.
- The license expression again.

## 2025.07.24

### Added

- Conversion support for the `fmp` format.

### Changed

- Simplified file handling by taking in both a path and file-like object.
- Renamed encode, decode, read, and write functions.
- Change from `MIT` to `(MIT AND MIT-0)` for license expression.
- Switch to calendar versioning.
- Use a bidirectional dictionary instead of a list for the `fpd` format.

### Removed

- Python 3.9 support following [Pallets](https://palletsprojects.com/).

## 0.3.0 - 2025-07-19

### Added

- Tox for testing project to test multiple python environments locally.

### Changed

- Use `StringIO` for converting `mtx` to XML.
- Reading `mtx` character entries correctly.
- Read from file methods to read from path for `mtx`.

### Removed

- Pretty printing when converting `mtx` to XML.
- Support for 64-bit `mtx` format that are on Switch, PS4, Xbox One, and PC.

## 0.2.0 - 2025-07-18

### Added

- A way to run the project using `runpy` or `python -m legacy_puyo_tools`.
- Testing infrastructure to avoid regressions.
- Tests for the `fpd` module.
- Custom `__str__` functions to avoid re-encoding.

### Changed

- Backport project to Python 3.9+ to follow Debian LTS.
- Take in strings and Path-Like objects for path arguments.
- `main` to `app` for the command line interface.

## 0.1.0 - 2025-07-16

### Added

- Installation, usage, and supported games sections in README.md.
- Information about the `fmp` format (#2).

### Changed

- Rewrite the command line interface to use [`cloup`] instead of `argparse`.
- Update formats.md with current support progress.

[`cloup`]: https://cloup.readthedocs.io

## 0.0.1 - 2025-07-15

### Added

- Basic extraction support for the `mtx` format.
- Full conversion support for the `fpd` format.
