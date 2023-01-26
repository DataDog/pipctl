#!/usr/bin/env python3
import os

import yaml
from click.testing import CliRunner
from pipctl.cli import cli
from pipctl import CONFIG_NAME

from .base import Base


class TestConfig(Base):
    """Test config file usage."""

    def test_cli_create(self) -> None:
        """Test creating and verifying configuration file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            assert CONFIG_NAME not in os.listdir(),\
                f"Configuration file already present in the current directory at {os.getcwd()}"

            result = runner.invoke(cli, ["config", "--verify"])  # No interactive mode.

            assert result.exit_code == 0
            assert CONFIG_NAME in os.listdir(), f"No configuration file was created in {os.getcwd()}"

            # Make sure the config can be parsed.
            with open(CONFIG_NAME) as f:
                yaml.safe_load(f)

