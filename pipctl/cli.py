#!/usr/bin/env python3

import logging
import os
import sys
import rich_click as click
import daiquiri
import yaml
import pkg_resources
from typing import Optional

import pipctl
import pip
from pipctl import Config
from pipctl import ConfigNotFound
from pipctl import ConfigError

_LOGGER = daiquiri.getLogger(pipctl.__title__)
daiquiri.setup(level=logging.INFO)


def _print_version(ctx: click.Context, _, value: str) -> None:
    """Print version and exit."""
    if not value or ctx.resilient_parsing:
        return

    click.echo(f"{pipctl.__title__}: {pipctl.__version__}")
    ctx.exit(0)


@click.group()
@click.option(
    "--debug/--no-debug",
    default=False,
    help="Run this tool in debug mode.",
)
@click.option(
    "--version",
    "-v",
    is_flag=True,
    is_eager=True,
    callback=_print_version,
    expose_value=False,
    help="Print version and exit.",
)
def cli(debug: bool = False) -> None:
    """Control pip resolution process."""
    if debug:
        _LOGGER.setLevel(logging.DEBUG)
        _LOGGER.debug("Debug mode is on")


@cli.command("config")
@click.option(
    "--config",
    type=str,
    help="File with additional configuration for generating constraints.",
    metavar=pipctl.CONFIG_NAME,
)
@click.option(
    "--verify",
    is_flag=True,
    help="Only verify the given configuration file; do not interact.",
)
def cli_config(config: Optional[str] = None, verify: bool = False) -> None:
    """Create and/or open configuration file for editing."""
    try:
        config = config or Config.get_config_file_path()
    except ConfigNotFound:
        _LOGGER.warning("No configuration file found")
        config = Config.create()
        _LOGGER.info("Created new configuration file at %s", config)

    if not verify:
        click.edit(filename=config)
        return

    try:
        Config.validate_file(config)
    except ConfigError as exc:
        _LOGGER.error("Failed to validate schema file: %s", exc)
        sys.exit(1)
    else:
        _LOGGER.info("Schema validation of configuration file %r passed", config)


@cli.command("report")
@click.option(
    "--config",
    type=str,
    help="File with additional configuration for generating constraints; try to find one if not provided explicitly.",
    metavar=pipctl.CONFIG_NAME,
)
def cli_report(config: Optional[str] = None) -> None:
    """Report environment information for debugging."""
    config_instance = None
    try:
        config_instance = Config.from_file(config)
    except Exception as exc:
        _LOGGER.warning("Failed to load configuration file: %s", str(exc))

    click.echo(
        yaml.safe_dump(
            {
                "config": config_instance.to_dict() if config_instance is not None else None,
                "config_path": config_instance.config_path if config_instance is not None else None,
                "cwd": os.getcwd(),
                "pip.version": pip.__version__,
                "piptools_version": pkg_resources.get_distribution("pip-tools").version,
                "python_version": ".".join(tuple(map(str, sys.version_info))),
                "version": pipctl.__version__,
            }
        )
    )


@cli.command("constraint")
@click.option(
    "--config",
    type=str,
    help="File with additional configuration for generating constraints; try to find one if not provided explicitly.",
    metavar=pipctl.CONFIG_NAME,
)
def cli_constraint(config: Optional[str] = None) -> None:
    """Resolve application dependencies respecting constraints created based on known vulnerabilities."""
    result = pipctl.constraints(Config.from_file(config))
    click.echo("\n".join(sorted(str(i.req) for i in result)))


__name__ == "__main__" and cli(auto_envvar_prefix=pipctl.__title__.upper())
