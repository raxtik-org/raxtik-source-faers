"""Official FDA FAERS/AEMS data connector, parser, and extractor for raxtik-etl."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Optional, Union

from raxtik_source_faers.adapter import FAERSAdapter
from raxtik_source_faers.client import FAERS
from raxtik_source_faers.fetcher import download_quarterly_archive, find_local_faers_files
from raxtik_source_faers.parser import clean_field_name, detect_table_type, parse_faers_ascii_file
from raxtik_source_faers.signatures.resolver import detect_archive_signature

__version__ = "0.1.0.dev0"


def build_package(
    release: str,
    output_dir: Optional[Union[str, Path]] = None,
    format: str = "both",
    delete_ascii: bool = True,
    download_dir: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """Downloads FDA FAERS quarterly archive, extracts ASCII files, builds DuckDB/Parquet package, and cleans up raw files.

    Args:
        release: Quarter identifier, e.g. '2004Q1' or '2024Q1'
        output_dir: Destination folder for DuckDB/Parquet packages (defaults to ~/.cache/raxtik/packages)
        format: Export format: 'both', 'duckdb', or 'parquet' (defaults to 'both')
        delete_ascii: Whether to delete downloaded raw ASCII archive after packaging (defaults to True)
        download_dir: Directory for temporary raw download (defaults to ~/.cache/raxtik/raw_archives)

    Returns:
        Dict with package metadata, paths, and quality metrics.
    """
    rel_clean = release.strip().upper()
    match = re.search(r"(\d{4})Q([1-4])", rel_clean)
    if not match:
        raise ValueError(
            f"Invalid FAERS release format: '{release}'. Expected format like '2004Q1'."
        )

    year = int(match.group(1))
    quarter = int(match.group(2))

    downloaded_zip = download_quarterly_archive(year=year, quarter=quarter, dest_dir=download_dir)

    from raxtik_etl.packaging.builder import build_quarterly_package

    return build_quarterly_package(
        release=rel_clean,
        zip_path=downloaded_zip,
        source_name="faers",
        adapter=FAERSAdapter(),
        output_dir=Path(output_dir) if output_dir else None,
        format=format,
        delete_ascii=delete_ascii,
    )


__all__ = [
    "FAERS",
    "FAERSAdapter",
    "build_package",
    "download_quarterly_archive",
    "find_local_faers_files",
    "clean_field_name",
    "detect_table_type",
    "parse_faers_ascii_file",
    "detect_archive_signature",
    "__version__",
]
