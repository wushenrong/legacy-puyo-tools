# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

- A way to run the project using `runpy` or `python -m legacy_puyo_tools`.
- Testing infrastructure to avoid regressions.
- Custom `__str__` functions to avoid re-encoding.

### Changed

- Backport project to Python 3.9 to follow Debian LTS.
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
