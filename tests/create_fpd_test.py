"""Testing creating fpd formats."""

from pathlib import Path

from click.testing import CliRunner

from legacy_puyo_tools.cli import create_fpd
from legacy_puyo_tools.fpd import BOM_UTF16_LE, ENCODING


def test_create_fpd() -> None:
    """Test creating an FPD file."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        with Path("sample_data.txt").open("w", encoding=ENCODING) as f:
            f.write(BOM_UTF16_LE.decode(ENCODING))
            # TODO: Write longer sample data
            f.write("ABC")

        result = runner.invoke(create_fpd, ["sample_data.txt"])

        with Path("sample_data.fpd").open("rb") as f:
            assert f.read() == b"A\x00\x00B\x00\x00C\x00\x00"

        assert result.exit_code == 0
