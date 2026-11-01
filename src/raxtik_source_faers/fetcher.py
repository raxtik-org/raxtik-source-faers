"""Archive fetcher and local file discovery for FDA FAERS quarterly datasets."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Union

import requests
from raxtik_etl.sources import (
    download_file,
    find_files_by_entity,
    format_quarter,
    is_valid_quarter,
    normalize_quarter,
    parse_quarter,
    stream_download,
)

from raxtik_source_faers.constants import (
    DEFAULT_HTTP_TIMEOUT,
    DEFAULT_RAW_CACHE_DIR,
    FAERS_BASE_URL,
    TABLE_PREFIX_TO_ENTITY,
)


def find_local_faers_files(directory: Union[Path, str]) -> Dict[str, List[Path]]:
    """Search directory recursively for FAERS ASCII files (.txt).

    Returns:
        Dict mapping canonical entity name ('demo', 'drug', 'reac', 'outc', 'indi', 'ther', 'rpsr')
        to a sorted list of Path objects.
    """
    return find_files_by_entity(directory, TABLE_PREFIX_TO_ENTITY, pattern="*.txt")


def download_quarterly_archive(
    year: Optional[int] = None,
    quarter: Optional[int] = None,
    dest_dir: Optional[Union[Path, str]] = None,
    overwrite: bool = False,
    timeout: int = DEFAULT_HTTP_TIMEOUT,
    *,
    data_period: Optional[str] = None,
) -> Path:
    """Download official FDA FAERS/AERS ASCII zip archive for a given year & quarter.

    Handles historical and modern archive naming patterns:
    - modern FAERS: faers_ascii_YYYYqQ.zip / FAERS_ASCII_YYYYQQ.zip
    - legacy AERS: aers_ascii_YYYYqQ.zip / AERS_ASCII_YYYYQQ.zip

    Args:
        year: Year (e.g. 2004, 2012, 2024). Optional if data_period is provided.
        quarter: Quarter integer (1, 2, 3, or 4). Optional if data_period is provided.
        dest_dir: Destination folder to store the zip (defaults to cache directory).
        overwrite: Whether to re-download if the file already exists.
        timeout: HTTP request timeout in seconds.
        data_period: Optional quarterly period string (e.g. '2004Q1') as an alternative to year/quarter.

    Returns:
        Path to the downloaded .zip file.

    Raises:
        ValueError: If quarter is not 1, 2, 3, or 4, or arguments are missing.
        RuntimeError: If remote archive cannot be found.
    """
    if data_period is not None and (year is None or quarter is None):
        parsed_year, parsed_quarter = parse_quarter(data_period)
        year = year or parsed_year
        quarter = quarter or parsed_quarter

    if year is None or quarter is None:
        raise ValueError("Must provide either (year, quarter) or data_period.")

    if quarter not in (1, 2, 3, 4):
        raise ValueError(f"Invalid quarter: {quarter}. Must be 1, 2, 3, or 4.")

    out_dir = Path(dest_dir) if dest_dir else DEFAULT_RAW_CACHE_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    candidates = [
        f"faers_ascii_{year}q{quarter}.zip",
        f"FAERS_ASCII_{year}Q{quarter}.zip",
        f"aers_ascii_{year}q{quarter}.zip",
        f"AERS_ASCII_{year}Q{quarter}.zip",
    ]

    target_zip = out_dir / candidates[0]
    if target_zip.exists() and not overwrite:
        return target_zip

    session = requests.Session()
    response = None
    selected_url = None

    for candidate in candidates:
        url = f"{FAERS_BASE_URL}/{candidate}"
        try:
            resp = session.get(url, stream=True, timeout=timeout)
            if resp.status_code == 200:
                response = resp
                selected_url = url
                target_zip = out_dir / candidate
                break
        except requests.RequestException:
            continue

    if response is None or selected_url is None:
        raise RuntimeError(
            f"Could not find FDA FAERS/AERS archive for {year}Q{quarter} at {FAERS_BASE_URL}"
        )

    stream_download(response, target_zip)
    return target_zip


__all__ = [
    "download_file",
    "download_quarterly_archive",
    "find_files_by_entity",
    "find_local_faers_files",
    "format_quarter",
    "is_valid_quarter",
    "normalize_quarter",
    "parse_quarter",
    "stream_download",
]
