"""Package builder utilities for FDA FAERS datasets."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Union

from raxtik_etl.packaging.builder import PackageFormat, build_quarterly_package
from raxtik_etl.sources import normalize_quarter

from raxtik_source_faers.adapter import FAERSAdapter
from raxtik_source_faers.constants import DEFAULT_RAW_CACHE_DIR, SOURCE_NAME


def build_package(
    data_period: str,
    output_dir: Optional[Union[str, Path]] = None,
    format: Union[PackageFormat, str] = PackageFormat.BOTH,
    delete_ascii: bool = True,
    download_dir: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """Downloads FDA FAERS quarterly archive, extracts ASCII files, builds DuckDB/Parquet package, and cleans up raw files.

    Args:
        data_period: Quarter identifier, e.g. '2004Q1' or '2024Q1'
        output_dir: Destination folder for DuckDB/Parquet packages (defaults to ~/.cache/raxtik/packages)
        format: Export format: PackageFormat or 'both', 'duckdb', 'parquet' (defaults to PackageFormat.BOTH)
        delete_ascii: Whether to delete downloaded raw ASCII archive after packaging (defaults to True)
        download_dir: Directory for temporary raw download (defaults to ~/.cache/raxtik/raw_archives)

    Returns:
        Dict with package metadata, paths, and quality metrics.

    Raises:
        ValueError: If data_period format is invalid.
    """
    canonical_period = normalize_quarter(data_period)

    adapter = FAERSAdapter()
    dest_path = Path(download_dir) if download_dir else DEFAULT_RAW_CACHE_DIR
    downloaded_zip = adapter.fetch_archive(data_period=canonical_period, dest_dir=dest_path)

    return build_quarterly_package(
        data_period=canonical_period,
        zip_path=downloaded_zip,
        source_name=SOURCE_NAME,
        adapter=adapter,
        output_dir=Path(output_dir) if output_dir else None,
        format=format,
        delete_ascii=delete_ascii,
    )
