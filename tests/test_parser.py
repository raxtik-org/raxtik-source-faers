"""Unit tests for FAERS $-delimited ASCII parser."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from raxtik_source_faers.parser import (
    clean_field_name,
    detect_table_type,
    parse_faers_ascii_file,
)


@pytest.mark.parametrize(
    ("filename", "prefix_mapping", "expected"),
    [
        ("DEMO04Q1.txt", None, "demo"),
        ("drug24q1.txt", None, "drug"),
        ("/path/to/REAC12Q4.TXT", None, "reac"),
        ("OUTC20Q3.txt", None, "outc"),
        ("INDI05Q2.txt", None, "indi"),
        ("THER14Q1.txt", None, "ther"),
        ("RPSR19Q4.txt", None, "rpsr"),
        ("unknown_file.txt", None, None),
        ("VAERSDATA_2024.csv", {"VAERSDATA": "demo"}, "demo"),
        ("UNKNOWN.csv", {"VAERSDATA": "demo"}, None),
    ],
)
def test_detect_table_type(
    filename: str, prefix_mapping: dict[str, str] | None, expected: str | None
) -> None:
    """Verify table prefix detection across standard and custom prefix mappings."""
    kwargs: dict[str, Any] = {"prefix_mapping": prefix_mapping} if prefix_mapping else {}
    assert detect_table_type(filename, **kwargs) == expected


@pytest.mark.parametrize(
    ("raw_name", "expected"),
    [
        ("PRIMARYID", "primaryid"),
        ("  CASE_ID  ", "case_id"),
        ("FOLL-SEQ#", "foll_seq"),
        ("__WT_COD__", "wt_cod"),
    ],
)
def test_clean_field_name(raw_name: str, expected: str) -> None:
    """Verify field normalization to lowercase snake_case."""
    assert clean_field_name(raw_name) == expected


@pytest.mark.parametrize(
    ("filename", "content", "expected_type", "expected_subset"),
    [
        (
            "DEMO24Q1.txt",
            "PRIMARYID$CASEID$SEX$AGE$AGE_COD\n10000001$10000001$F$45$YR\n10000002$10000002$M$62$YR\n",
            "demo",
            {"primaryid": "10000001", "sex": "F", "_table_type": "demo"},
        ),
        (
            "DRUG24Q1.txt",
            "PRIMARYID$DRUG_SEQ$DRUGNAME\n10000001$1$ASPIRIN\n",
            "drug",
            {
                "primaryid": "10000001",
                "drug_seq": "1",
                "drugname": "ASPIRIN",
                "_table_type": "drug",
            },
        ),
    ],
)
def test_parse_faers_ascii_file(
    tmp_path: Path,
    filename: str,
    content: str,
    expected_type: str,
    expected_subset: dict[str, Any],
) -> None:
    """Verify standard dollar-delimited ASCII file streaming parsing across entity files."""
    sample_file = tmp_path / filename
    sample_file.write_text(content)
    records = list(parse_faers_ascii_file(sample_file))
    assert len(records) >= 1
    assert records[0]["_table_type"] == expected_type
    for k, v in expected_subset.items():
        assert records[0][k] == v
