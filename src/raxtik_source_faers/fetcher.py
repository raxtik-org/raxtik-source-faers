"""Archive fetcher and local file discovery for FDA FAERS quarterly datasets."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Union

import requests
from tqdm import tqdm

from raxtik_source_faers.parser import detect_table_type

FAERS_BASE_URL: str = "https://fis.fda.gov/content/Exports"


def find_local_faers_files(directory: Union[Path, str]) -> Dict[str, List[Path]]:
    """Search directory recursively for FAERS ASCII files (.txt).

    Returns:
        Dict mapping canonical entity name ('demo', 'drug', 'reac', 'outc', 'indi', 'ther', 'rpsr')
        to a sorted list of Path objects.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return {}

    categorized: Dict[str, List[Path]] = {
        "demo": [],
        "drug": [],
        "reac": [],
        "outc": [],
        "indi": [],
        "ther": [],
        "rpsr": [],
    }

    for file_path in dir_path.rglob("*.txt"):
        tbl_type = detect_table_type(file_path)
        if tbl_type and tbl_type in categorized:
            categorized[tbl_type].append(file_path)

    return {k: sorted(v) for k, v in categorized.items() if v}


def download_quarterly_archive(
    year: int,
    quarter: int,
    dest_dir: Optional[Union[Path, str]] = None,
    overwrite: bool = False,
) -> Path:
    """Download official FDA FAERS/AERS ASCII zip archive for a given year & quarter.

    Handles historical and modern archive naming patterns:
    - modern FAERS: faers_ascii_YYYYqQ.zip / FAERS_ASCII_YYYYQQ.zip
    - legacy AERS: aers_ascii_YYYYqQ.zip / AERS_ASCII_YYYYQQ.zip

    Args:
        year: Year (e.g. 2004, 2012, 2024).
        quarter: Quarter integer (1, 2, 3, or 4).
        dest_dir: Destination folder to store the zip (defaults to current working directory).
        overwrite: Whether to re-download if the file already exists.

    Returns:
        Path to the downloaded .zip file.
    """
    if quarter not in (1, 2, 3, 4):
        raise ValueError(f"Invalid quarter: {quarter}. Must be 1, 2, 3, or 4.")

    out_dir = Path(dest_dir) if dest_dir else Path.cwd()
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
            resp = session.get(url, stream=True, timeout=30)
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

    total_size = int(response.headers.get("content-length", 0))
    with (
        open(target_zip, "wb") as f,
        tqdm(
            desc=f"Downloading {target_zip.name}",
            total=total_size,
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar,
    ):
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)
                bar.update(len(chunk))

    return target_zip
