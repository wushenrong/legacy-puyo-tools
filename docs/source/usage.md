# Usage

```{todo} Create a more comprehensive usage page.
```

First check you have the latest version of `legacy-puyo-tools`:

```bash
legacy-puyo-tools --version
```

## Convert

To convert a format, use the `convert` sub-command and the format you want to
convert.

Example: `mtx` file to an editable XML file using a `fpd` file.

```bash
legacy-puyo-tools convert mtx --output custom_als.mtx --fpd puyo14.fpd als.xml
```

## Create

To create a format, use the `create` sub-command and the format you want to
create.

Example: Create a `fpd` file from a UTF-16 little-endian encoded text file.

```bash
legacy-puyo-tools create fpd puyo14.txt
```

You can use the `--help` flag to see what sub-commands and options are
available.
