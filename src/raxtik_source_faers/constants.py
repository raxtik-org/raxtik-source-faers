"""Centralized Constants and Configuration for raxtik-source-faers.

Defines all immutable entity names, file prefixes, URLs, and protocol defaults
used throughout the FDA FAERS extraction and adapter pipeline.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final, Mapping, Tuple

# Source Connector Identity & Protocols
SOURCE_NAME: Final[str] = "faers"
CANONICAL_SCHEMA_VERSION: Final[str] = "1.0.0"
PROTOCOL_VERSION: Final[str] = "1.0"

# Canonical Table Entities
CANONICAL_TABLES: Final[Tuple[str, ...]] = (
    "demo",
    "drug",
    "reac",
    "outc",
    "indi",
    "ther",
    "rpsr",
)

# FDA ASCII Physical Archive File Prefixes
TABLE_PREFIXES: Final[Tuple[str, ...]] = (
    "DEMO",
    "DRUG",
    "REAC",
    "OUTC",
    "RPSR",
    "THER",
    "INDI",
)

# Prefix to Entity Mapping
TABLE_PREFIX_TO_ENTITY: Final[Mapping[str, str]] = {
    "DEMO": "demo",
    "DRUG": "drug",
    "REAC": "reac",
    "OUTC": "outc",
    "RPSR": "rpsr",
    "THER": "ther",
    "INDI": "indi",
}

# Reference / Codelist Tables Delivered with Packages
REFERENCE_TABLE_NAMES: Final[Tuple[str, ...]] = (
    "_code_outcomes",
    "_code_roles",
    "_code_occupations",
    "_code_report_sources",
    "_code_dechallenge",
    "_code_rechallenge",
)

# Upstream Distribution & Network Defaults
DEFAULT_HF_REPO: Final[str] = "raxtik-org/faers-safety-database"
FAERS_BASE_URL: Final[str] = "https://fis.fda.gov/content/Exports"
DEFAULT_HTTP_TIMEOUT: Final[int] = int(os.getenv("FAERS_HTTP_TIMEOUT", "60"))
DEFAULT_RAW_CACHE_DIR: Final[Path] = Path(
    os.getenv("FAERS_CACHE_DIR", Path.home() / ".cache" / "raxtik" / "raw_archives")
)
