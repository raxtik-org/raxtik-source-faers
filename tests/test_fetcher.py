"""Unit tests for FAERS archive fetcher and file discovery."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from raxtik_source_faers.fetcher import (
    download_quarterly_archive,
    find_files_by_entity,
    find_local_faers_files,
    format_quarter,
    is_valid_quarter,
    normalize_quarter,
    parse_quarter,
)


@pytest.mark.parametrize(
    ("raw_input", "expected_tuple", "expected_normalized"),
    [
        ("2004Q1", (2004, 1), "2004Q1"),
        ("2012q4", (2012, 4), "2012Q4"),
        ("faers_ascii_2024q1.zip", (2024, 1), "2024Q1"),
        ("aers_ascii_2008Q2.zip", (2008, 2), "2008Q2"),
        ("aers_ascii_2006q3.zip", (2006, 3), "2006Q3"),
    ],
)
def test_quarterly_valid_operations(
    raw_input: str, expected_tuple: tuple[int, int], expected_normalized: str
) -> None:
    """Verify quarterly parsing, formatting, normalization, and validity check."""
    assert parse_quarter(raw_input) == expected_tuple
    assert format_quarter(*expected_tuple) == expected_normalized
    assert normalize_quarter(raw_input) == expected_normalized
    assert is_valid_quarter(raw_input) is True


@pytest.mark.parametrize(
    "invalid_input",
    ["invalid_quarter", "2004Q5", "2004", "Q1", "", "2024Q0", "2024Q-1"],
)
def test_quarterly_invalid_inputs(invalid_input: str) -> None:
    """Verify invalid quarterly formats fail validation and normalization."""
    assert is_valid_quarter(invalid_input) is False
    with pytest.raises(ValueError, match=r"Invalid quarterly format"):
        parse_quarter(invalid_input)
    with pytest.raises(ValueError, match=r"Invalid quarterly format"):
        normalize_quarter(invalid_input)


@pytest.mark.parametrize(
    ("files", "mapping", "pattern", "expected_counts"),
    [
        (
            ["DEMO04Q1.txt", "DRUG04Q1.txt", "REAC04Q1.txt", "random.txt"],
            None,
            "*.txt",
            {"demo": 1, "drug": 1, "reac": 1},
        ),
        (
            ["VAERSDATA_2020.csv", "VAERSSYMPTOMS_2020.csv", "VAERSVAX_2020.csv", "extra.txt"],
            {"VAERSDATA": "demo", "VAERSSYMPTOMS": "reac", "VAERSVAX": "drug"},
            "*.csv",
            {"demo": 1, "reac": 1, "drug": 1},
        ),
    ],
)
def test_file_discovery_by_entity(
    tmp_path: Path,
    files: list[str],
    mapping: dict[str, str] | None,
    pattern: str,
    expected_counts: dict[str, int],
) -> None:
    """Verify local file categorization via default FAERS detector or generic prefix mapping."""
    sub = tmp_path / "data"
    sub.mkdir()
    for fname in files:
        (sub / fname).write_text("header\n")

    res = (
        find_local_faers_files(tmp_path)
        if mapping is None
        else find_files_by_entity(tmp_path, prefix_to_entity=mapping, pattern=pattern)
    )
    for entity, count in expected_counts.items():
        assert entity in res
        assert len(res[entity]) == count
    assert "random" not in res and "extra" not in res


@pytest.mark.parametrize(
    ("kwargs", "match_pattern"),
    [
        ({}, r"Must provide either \(year, quarter\) or data_period"),
        ({"year": 2024, "quarter": 5}, r"Invalid quarter: 5"),
        ({"year": 2024, "quarter": 0}, r"Invalid quarter: 0"),
        ({"year": 2024, "quarter": -1}, r"Invalid quarter: -1"),
        ({"data_period": "invalid_q"}, r"Invalid (?:quarterly|FAERS).*format"),
    ],
)
def test_download_quarterly_archive_validation(kwargs: dict[str, Any], match_pattern: str) -> None:
    """Verify download parameter validation for missing args and out-of-range quarters."""
    with pytest.raises(ValueError, match=match_pattern):
        download_quarterly_archive(**kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"year": 2024, "quarter": 1},
        {"data_period": "2024Q1"},
    ],
)
def test_download_quarterly_archive_skip_existing(tmp_path: Path, kwargs: dict[str, Any]) -> None:
    """Verify skip-download logic when target zip already exists via year/quarter and data_period."""
    existing_zip = tmp_path / "faers_ascii_2024q1.zip"
    existing_zip.write_bytes(b"PK\x05\x06" + b"\x00" * 18)

    returned = download_quarterly_archive(dest_dir=tmp_path, overwrite=False, **kwargs)
    assert returned == existing_zip
