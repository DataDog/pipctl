#!/usr/bin/env python3

import os
import shutil

import attr
import daiquiri
import yaml
from openapi_schema_validator import OAS30Validator
from openapi_schema_validator import validate

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ._exceptions import ConfigValidationError
from ._exceptions import ConfigNotFound
from ._exceptions import ConfigParseError

_LOGGER = daiquiri.getLogger(__name__)

# Maximum number of traversals allowed when searching for config.yaml.
_MAX_DIR_TRAVERSAL = 42
CONFIG_NAME = os.getenv("PIPCTL_CONFIG_NAME", "pipctl.yaml")


@attr.s(slots=True)
class Config:
    """Representation of configuration file as loaded from disk."""

    # Group data/ directory files.
    _DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    _TEMPLATE_CONFIG_PATH = os.path.join(_DATA_DIR, "templateConfig.yaml")
    _CONFIG_SCHEMA_PATH = os.path.join(_DATA_DIR, "configSchema.json")

    config_path = attr.ib(type=str)
    requirements_file = attr.ib(type=str)
    constraints_file = attr.ib(type=Optional[str], default=None)
    acceptable_vulnerabilities = attr.ib(type=List[str], default=attr.Factory(list))

    @staticmethod
    def get_config_file_path() -> str:
        """Get a path to a configuration file."""
        directory = os.getcwd()
        for _ in range(_MAX_DIR_TRAVERSAL):
            config_path = os.path.join(directory, CONFIG_NAME)
            if os.path.exists(config_path):
                _LOGGER.debug("Using configuration file %s", config_path)
                return config_path
            # cd ..
            directory = os.path.abspath(os.path.join(directory, os.path.pardir))

        raise ConfigNotFound(
            f"No configuration file {CONFIG_NAME!r} found in {os.getcwd()!r} or any parent directories"
        )

    @classmethod
    def from_file(cls, config_path: Optional[str] = None) -> "Config":
        """Instantiate config from a file."""
        config_path = config_path or cls.get_config_file_path()

        try:
            with open(config_path) as f:
                config_content = yaml.safe_load(f)
        except Exception as exc:
            raise ConfigParseError(f"Failed to load config file {config_path!r}") from exc

        return Config(
            config_path=config_path,
            requirements_file=config_content["requirements_file"],
            constraints_file=config_content.get("constraints_file"),
            acceptable_vulnerabilities=config_content.get("acceptable_vulnerabilities") or [],
        )

    @classmethod
    def create(cls, directory: Optional[str] = None, config_name: str = CONFIG_NAME) -> str:
        """Create configuration file from a template and return its path."""
        directory = directory or os.getcwd()
        config_path = os.path.join(directory, config_name)
        _LOGGER.debug("Using template %r for new configuration file", cls._TEMPLATE_CONFIG_PATH)
        shutil.copyfile(cls._TEMPLATE_CONFIG_PATH, config_path)
        return config_path

    @classmethod
    def validate_file(cls, file_path: str) -> None:
        """Validate the given configuration file."""
        with open(cls._CONFIG_SCHEMA_PATH) as f:
            schema = yaml.safe_load(f)

        with open(file_path) as f:
            config_content = yaml.safe_load(f)

        try:
            validate(config_content, schema, cls=OAS30Validator)
        except Exception as exc:
            raise ConfigValidationError(f"Failed to validate configuration file: {str(exc)}") from exc

    def to_dict(self) -> Dict[str, Any]:
        """Translate config instance into a directory."""
        config_dict = attr.asdict(self)
        config_dict.pop("config_path")  # We do not store path as part of configuration file content.
        return config_dict
