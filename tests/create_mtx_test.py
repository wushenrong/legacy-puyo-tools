"""Tests for creating mtx formats."""

from pathlib import Path

from click.testing import CliRunner

from legacy_puyo_tools.cli import create_mtx


def test_create_mtx() -> None:
    """Test creating an MTX file."""
    # TODO: Implement the actual test logic for creating an MTX file once it has
    # been implemented.
    # This is a placeholder to ensure the test runs without errors.
    runner = CliRunner()

    with runner.isolated_filesystem():
        with Path("example.fpd").open("wb") as f:
            f.write(b"A\x00\x00B\x00\x00C\x00\x00")

        with Path("test.xml").open("w", encoding="utf-8") as f:
            f.write("<mtx></mtx>")

        result = runner.invoke(
            create_mtx, ["--fpd", "example.fpd", "test.xml", "--output", "test.mtx"]
        )

    assert result.exit_code == 1
