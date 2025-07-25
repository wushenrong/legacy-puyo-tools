# Legacy Puyo Tools

A command line tool for modding older Puyo Puyo games (Yes, the name is using a
[reversed naming scheme](https://github.com/microsoft/WSL)).

## Installation

Install [Python](https://www.python.org/) 3.10 or later, preferably the latest
version.

`legacy-python-tools` is published to
[PyPI](https://pypi.org/project/legacy-puyo-tools/). It is recommended to
install tools from PyPI into an isolated Python environment.

You can use [`pipx`](https://pipx.pypa.io):

```bash
pipx install legacy-python-tools
# Or to run the cli without installing legacy-python-tools
pipx run legacy-python-tools
```

Or [`uv`](https://docs.astral.sh/uv):

```bash
uv tool install legacy-python-tools
# Or to run the cli without installing legacy-python-tools
uv tool run legacy-python-tools
# Or the shorter uvx
uvx legacy-python-tools
```

And of course, you can use good old pip in a virtual Python environment using
[`virualenv`](https://virtualenv.pypa.io) or the built-in `venv` library:

```bash
# Create a virtual python environment
python -m venv .venv
# Activate the virtual environment
./.venv/Scripts/activate
# Install legacy-python-tools
python -m pip install legacy-python-tools
```

## Usage

Create a `fpd` file from a UTF-16 little-endian encoded text file.

```bash
legacy-puyo-tools create fpd puyo14.txt
```

Or convert a `mtx` file to an editable XML file using a `fpd` file.

```bash
legacy-puyo-tools convert mtx --output custom_als.mtx --fpd puyo14.fpd als.xml
```

You can use the `--help` flag to see what sub-commands and options are
available.

## Supported Games

This tool will try to support formats from the following Puyo games:

- Puyo Puyo! 15th Annversivery
- Puyo Puyo 7
- Puyo Puyo!! 20th Annversivery (If there is demand)

See
[Formats](https://github.com/wushenrong/legacy-puyo-tools/blob/main/formats.md)
for detailed information about these formats, and the current progress on
creating and converting them.

## Why

The [Puyo Text Editor][puyo-text-editor] can already do what `legacy-puyo-tools`
does and is the inspiration of this tool, but there are advantages to rewrite it
in Python:

[puyo-text-editor]: https://github.com/nickworonekin/puyo-text-editor

- Better cross compatibility with Linux.
- Easier migration when upgrade away from end of life language versions.
- Formats are stored in an intermediate representation before conversion.

## Contributing

If you want to contribute to the project check out
[Contributing](https://github.com/wushenrong/legacy-puyo-tools/blob/main/CONTRIBUTING.md).

## License

Under the MIT License. Based on [Puyo Text Editor][puyo-text-editor] which is
also under the MIT License. Some code is generated using AI in which they are
licensed under the MIT-0 License.
