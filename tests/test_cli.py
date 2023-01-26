#!/usr/bin/env python3


from .base import Base
from click.testing import CliRunner
from pipctl.cli import cli
import pipctl


class TestCLI(Base):
    """Test invocation of CLI."""

    def test_version(self):
        """Test obtaining CLI version."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert result.output == f"{pipctl.__title__}: {pipctl.__version__}\n"

    def test_help(self) -> None:
        """Test obtaining help message."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output
