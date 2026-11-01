"""Integration test for FAERSAdapter extracting into DuckDB."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import duckdb
import pytest
from raxtik_etl.sources.protocol import SourceArtifact

from raxtik_source_faers.adapter import FAERSAdapter

CACHE_2004Q1 = (
    Path(
        os.environ.get(
            "FAERS_CACHE_DIR", Path(__file__).parents[2] / "raxtik-etl/data/raw/archives_cache"
        )
    )
    / "2004q1_ascii.zip"
)


def test_faers_adapter_extraction(tmp_path: Path):
    """Verify that FAERSAdapter extracts 2004Q1 and populates all 7 canonical tables."""
    if not CACHE_2004Q1.exists():
        return  # Skip if cache not available in CI environment

    db_path = tmp_path / "test_extract.duckdb"
    con = duckdb.connect(str(db_path))

    adapter = FAERSAdapter()
    assert adapter.source_name == "faers"

    artifact = SourceArtifact(path=CACHE_2004Q1, data_period="2004Q1")
    result = adapter.extract_and_load(con, artifact)

    assert result.source_name == "faers"
    assert result.data_period == "2004Q1"
    assert result.signature_id == "S1"
    assert result.row_counts == {
        "demo": 65902,
        "drug": 235361,
        "reac": 264410,
        "outc": 57592,
        "indi": 78639,
        "ther": 84964,
        "rpsr": 78306,
    }

    # Verify reference tables delivered
    for ref_tbl in [
        "_code_outcomes",
        "_code_roles",
        "_code_occupations",
        "_code_report_sources",
        "_code_dechallenge",
        "_code_rechallenge",
    ]:
        assert ref_tbl in result.reference_tables
    assert len(result.reference_tables["_code_outcomes"]) == 7

    con.close()


def test_faers_adapter_missing_archive(tmp_path: Path):
    con = duckdb.connect()
    adapter = FAERSAdapter()
    artifact = SourceArtifact(path=tmp_path / "missing.zip", data_period="2004Q1")
    with pytest.raises(FileNotFoundError, match=r"^FAERS source archive not found at .*"):
        adapter.extract_and_load(con, artifact)
    con.close()


@pytest.mark.parametrize(
    ("data_period", "expected_err"),
    [
        ("", r"^Must provide data_period"),
        ("invalid_quarter", r"^Invalid data_period format for FAERS:"),
    ],
)
def test_faers_adapter_fetch_validation(tmp_path: Path, data_period: str, expected_err: str):
    adapter = FAERSAdapter()
    with pytest.raises(ValueError, match=expected_err):
        adapter.fetch_archive(data_period, dest_dir=tmp_path)


@pytest.mark.parametrize(
    ("method_name", "args", "expected_eval"),
    [
        ("supports_schema", ("1.0.0",), lambda res: res is True),
        ("supports_schema", ("2.0.0",), lambda res: res is False),
        ("supports_schema", ("unknown_schema",), lambda res: res is False),
        ("normalize_data_period", ("2004q1",), lambda res: res == "2004Q1"),
        ("get_migrations", (), lambda res: res == []),
        ("get_summary_views_sql", (), lambda res: "case_adverse_events_summary" in res),
    ],
)
def test_faers_adapter_stubs_and_helpers(method_name: str, args: tuple, expected_eval: Any) -> None:
    """Verify inherited BaseSourceAdapter stubs and helper methods on FAERSAdapter."""
    adapter = FAERSAdapter()
    assert expected_eval(getattr(adapter, method_name)(*args))
