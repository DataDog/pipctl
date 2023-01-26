#!/usr/bin/env python3

from click.testing import CliRunner
from pipctl.cli import cli
from pipctl import CONFIG_NAME

from .base import Base


class TestConstraints(Base):
    """Test resolution using constraint."""

    def test_cli_constraint(self) -> None:
        """Test calling constraint in CLI."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("requirements.txt", "w") as f:
                f.write("micropipenv<=1.0.0\n")

            with open(CONFIG_NAME, "w") as f:
                f.write("ignore_vulnerabilities: []\nrequirements_file: ./requirements.txt\n")

            result = runner.invoke(cli, ["constraint"])

            assert result.exit_code == 0
            assert result.stdout == "micropipenv==1.0.0\n"

    def test_constraint_acceptable(self) -> None:
        """Test constraining the resolution process with acceptable vulnerabilities."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("requirements.txt", "w") as f:
                f.write("urllib3==1.26.0\n")

            with open(CONFIG_NAME, "w") as f:
                f.write(
                    "acceptable_vulnerabilities: [GHSA-5phf-pp7p-vc2r, GHSA-q2q7-5pp4-w6pg]\n"
                    "requirements_file: ./requirements.txt\n"
                )

            result = runner.invoke(cli, ["constraint"])

            assert result.exit_code == 0
            output = [i for i in result.stdout.splitlines() if not i.startswith("WARNING")]
            assert output == ["urllib3==1.26.0"]

    def test_constraint_no_resolution(self) -> None:
        """Test constraining the resolution process but no resolution is found."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("requirements.txt", "w") as f:
                f.write("urllib3==1.26.0\n")

            with open(CONFIG_NAME, "w") as f:
                # GHSA-q2q7-5pp4-w6pg prevents finding a resolution.
                f.write("acceptable_vulnerabilities: [GHSA-5phf-pp7p-vc2r]\nrequirements_file: ./requirements.txt\n")

            result = runner.invoke(cli, ["constraint"])

            assert result.exit_code == 1
            assert "ERROR: Cannot install urllib3!=1.26.0 and urllib3==1.26.0 " \
                   "because these package versions have conflicting dependencies." in result.stdout
