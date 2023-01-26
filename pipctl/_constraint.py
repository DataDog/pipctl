#!/usr/bin/env python3

import os
import daiquiri
from typing import Generator
from ._config import Config
from ._osv import osv_vulnerabilities
from piptools.resolver import BacktrackingResolver
from piptools.locations import CACHE_DIR
from piptools.repositories import PyPIRepository
from pip_requirements_parser import RequirementsFile
from pip_requirements_parser import InstallRequirement as InstallRequirementParser
from pip._internal.req import InstallRequirement
from pip._vendor.packaging.requirements import Requirement

_LOGGER = daiquiri.getLogger(__name__)
_VULNERABILITY_URL = os.getenv("PIPCTL_OSV_VULN_URL", "https://osv.dev/vulnerability/{}")


def constraints(config: Config) -> Generator[Requirement, None, None]:
    """Compute constraints for the given project, considering inputs."""
    vulnerabilities = osv_vulnerabilities()

    constraints_listing = []
    for item in RequirementsFile.parse(config.requirements_file, include_nested=True, is_constraint=False):
        if isinstance(item, InstallRequirementParser):
            constraints_listing.append(
                InstallRequirement(
                    req=Requirement(str(item.req)),
                    comes_from=None,
                )
            )

    repository = PyPIRepository([], cache_dir=CACHE_DIR)

    acceptable_vulnerabilities = set(config.acceptable_vulnerabilities)
    stop_resolution = False
    result = []
    while not stop_resolution:
        resolver = BacktrackingResolver(
            constraints=constraints_listing,
            existing_constraints={},
            repository=repository,
        )
        result = resolver.resolve()
        # daiquiri.setup(level=logging.DEBUG)
        _LOGGER.debug("result: %r", result)  # XXX: logging is adjusted

        constraints_size = len(constraints_listing)

        for install_requirement in result:
            specifier, *_ = install_requirement.req.specifier._specs
            key = (install_requirement.req.name, specifier.version)

            for vulnerability_id, vulnerability_entry in vulnerabilities[key]:
                ignored = acceptable_vulnerabilities.intersection(vulnerability_entry)
                if ignored:
                    _LOGGER.warning("Ignoring vulnerability %r", vulnerability_id)
                    continue

                req = f"{install_requirement.req.name}!={specifier.version}"
                _LOGGER.warning(
                    "Adding constraint %r based on vulnerability %s - see %s",
                    req,
                    vulnerability_id,
                    _VULNERABILITY_URL.format(vulnerability_id),
                )
                constraints_listing.append(
                    InstallRequirement(
                        req=Requirement(req),
                        comes_from=None,
                    )
                )
                break

            if len(constraints_listing) != constraints_size:
                # A change to constraints was done, restart the resolution process with the new constraint added.
                break

        if len(constraints_listing) == constraints_size:
            # No changes to constraints made, we found a candidate.
            stop_resolution = True

    yield from result
