"""Official FDA FAERS/AEMS data connector, parser, and extractor for raxtik-etl."""

from __future__ import annotations

from raxtik_etl.packaging.builder import PackageFormat, compute_sha256
from raxtik_etl.sources import (
    clean_field_name,
    download_file,
    find_files_by_entity,
    format_quarter,
    is_valid_quarter,
    normalize_quarter,
    parse_delimited_file,
    parse_quarter,
    stream_download,
)

from raxtik_source_faers._version import __version__
from raxtik_source_faers.adapter import FAERSAdapter
from raxtik_source_faers.builder import build_package
from raxtik_source_faers.client import FAERS
from raxtik_source_faers.constants import (
    CANONICAL_SCHEMA_VERSION,
    CANONICAL_TABLES,
    DEFAULT_HF_REPO,
    DEFAULT_RAW_CACHE_DIR,
    FAERS_BASE_URL,
    PROTOCOL_VERSION,
    SOURCE_NAME,
    TABLE_PREFIXES,
)
from raxtik_source_faers.fetcher import (
    download_quarterly_archive,
    find_local_faers_files,
)
from raxtik_source_faers.parser import (
    detect_table_type,
    parse_faers_ascii_file,
)
from raxtik_source_faers.signatures.resolver import detect_archive_signature

__all__ = [
    "FAERS",
    "FAERSAdapter",
    "PackageFormat",
    "build_package",
    "clean_field_name",
    "compute_sha256",
    "detect_archive_signature",
    "detect_table_type",
    "download_file",
    "download_quarterly_archive",
    "find_files_by_entity",
    "find_local_faers_files",
    "format_quarter",
    "is_valid_quarter",
    "normalize_quarter",
    "parse_delimited_file",
    "parse_faers_ascii_file",
    "parse_quarter",
    "stream_download",
    "CANONICAL_SCHEMA_VERSION",
    "CANONICAL_TABLES",
    "DEFAULT_HF_REPO",
    "DEFAULT_RAW_CACHE_DIR",
    "FAERS_BASE_URL",
    "PROTOCOL_VERSION",
    "SOURCE_NAME",
    "TABLE_PREFIXES",
    "__version__",
]
