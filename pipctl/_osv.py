#!/usr/bin/env python3
import daiquiri
import os
import sys
import zipfile
import io
import json
import collections

from typing import Set
from typing import List
from typing import Tuple
from ._exceptions import OSVDownloadError
from ._exceptions import OSVError

if sys.version_info.minor < 9:
    from typing import DefaultDict
else:
    DefaultDict = collections.defaultdict  # type: ignore[misc]

import requests

_LOGGER = daiquiri.getLogger(__name__)


_OSV_PYPI_URL = os.getenv(
    "PIPCTL_OSV_PYPI_URL",
    "https://osv-vulnerabilities.storage.googleapis.com/PyPI/all.zip",
)


def osv_vulnerabilities(
    url: str = _OSV_PYPI_URL,
) -> DefaultDict[Tuple[str, str], List[Tuple[str, Set[str]]]]:
    """Get PyPI vulnerabilities from OSV."""
    _LOGGER.info("Downloading OSV database")
    _LOGGER.debug("Using OSV database from %r", url)
    response = requests.get(url)
    if response.status_code != 200:
        raise OSVDownloadError(
            f"Failed to download OSV database from {url!r} ({response.status_code}): {response.text}",
        )

    try:
        _LOGGER.debug("Extracting downloaded zip")
        zip = zipfile.ZipFile(io.BytesIO(response.content))
        _LOGGER.debug("Found %d vulnerability records", len(zip.namelist()))

        result: DefaultDict[Tuple[str, str], List[Tuple[str, Set[str]]]] = collections.defaultdict(list)
        for name in zip.namelist():
            _LOGGER.debug("Parsing vulnerability record with ID %s", name)
            vulnerability_record = json.loads(zip.read(name).decode())

            vulnerability_identifiers = set(vulnerability_record.get("aliases") or [])
            vulnerability_identifiers.add(vulnerability_record["id"])

            for affected in vulnerability_record["affected"]:
                for version in affected.get("versions") or []:
                    result[(affected["package"]["name"], version)].append(
                        (vulnerability_record["id"], vulnerability_identifiers)
                    )
    except Exception as exc:
        raise OSVError(f"Failed to obtain vulnerability information from OSV: {str(exc)}") from exc

    return result
