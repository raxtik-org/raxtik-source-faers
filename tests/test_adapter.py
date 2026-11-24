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
    with pytest.raises(FileNotFoundError):
        artifact = SourceArtifact(path=tmp_path / "missing.zip", data_period="2004Q1")
        adapter.extract_and_load(con, artifact)
    con.close()


def test_faers_adapter_invalid_data_period(tmp_path: Path):
    con = duckdb.connect()
    adapter = FAERSAdapter()
    dummy_zip = tmp_path / "non_quarterly_archive.zip"
    dummy_zip.write_bytes(b"PK\x05\x06" + b"\x00" * 18)
    artifact = SourceArtifact(path=dummy_zip, data_period=None)
    with pytest.raises(ValueError, match=r"Cannot determine valid FAERS quarterly data_period"):
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


def test_faers_case_resolution_ordering_rules():
    con = duckdb.connect(":memory:")
    adapter = FAERSAdapter()

    con.execute("""
        CREATE TABLE demo (
            primary_id VARCHAR,
            case_id VARCHAR,
            canonical_case_version INTEGER,
            latest_regulatory_date VARCHAR,
            manufacturer_date VARCHAR,
            event_date VARCHAR,
            standard_age_years DOUBLE,
            standard_sex_label VARCHAR,
            initial_or_followup_code VARCHAR,
            _data_period VARCHAR
        );
    """)

    test_rows = [
        ("101", "C1", 1, "20050101", "20041201", "20040101", 30.0, "Female", "I", "2004Q1"),
        ("102", "C1", 2, "20040601", "20040501", "20040101", 30.0, "Female", "F", "2004Q2"),
        ("201", "C2", 1, "20040101", "20031201", "20030101", 45.0, "Male", "I", "2004Q1"),
        ("202", "C2", 1, "20040901", "20040801", "20030101", 45.0, "Male", "F", "2004Q3"),
        ("301", "C3", 1, "20050101", "20041101", "20040101", 50.0, "Female", "I", "2005Q1"),
        ("302", "C3", 1, "20050101", "20041215", "20040101", 50.0, "Female", "F", "2005Q1"),
        ("401", "C4", 1, "20050101", "20041201", "20040101", 60.0, "Male", "I", "2005Q1"),
        ("409", "C4", 1, "20050101", "20041201", "20040101", 60.0, "Male", "I", "2005Q1"),
        ("501", "C5", None, "20060101", "20051201", "20050101", 65.0, "Female", "I", "2006Q1"),
        ("502", "C5", 1, "20050101", "20041201", "20050101", 65.0, "Female", "F", "2005Q1"),
        ("601", "C6", 1, None, None, "20050101", 70.0, "Male", "I", "2005Q1"),
        ("602", "C6", 1, "20050601", "20050501", "20050101", 70.0, "Male", "F", "2005Q2"),
    ]

    con.executemany("INSERT INTO demo VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", test_rows)
    con.execute(adapter.get_case_resolution_sql())

    resolved = dict(
        con.execute("SELECT case_id, primary_id FROM cases ORDER BY case_id").fetchall()
    )
    assert resolved["C1"] == "102"
    assert resolved["C2"] == "202"
    assert resolved["C3"] == "302"
    assert resolved["C4"] == "409"
    assert resolved["C5"] == "502"
    assert resolved["C6"] == "602"
    con.close()


def test_analytical_summary_view_zero_cartesian_fanout():
    con = duckdb.connect(":memory:")
    adapter = FAERSAdapter()

    con.execute("""
        CREATE TABLE demo (
            primary_id VARCHAR,
            case_id VARCHAR,
            canonical_case_version INTEGER,
            latest_regulatory_date VARCHAR,
            manufacturer_date VARCHAR,
            event_date VARCHAR,
            standard_age_years DOUBLE,
            standard_sex_label VARCHAR,
            _data_period VARCHAR
        );
        CREATE TABLE drug (
            primary_id VARCHAR,
            drug_seq INTEGER,
            reported_drug_name VARCHAR,
            structural_clean_drug_name VARCHAR,
            role_code VARCHAR
        );
        CREATE TABLE reac (
            primary_id VARCHAR,
            reported_reaction_term VARCHAR
        );
        CREATE TABLE outc (
            primary_id VARCHAR,
            outcome_code VARCHAR
        );
        CREATE TABLE _code_outcomes (
            code VARCHAR PRIMARY KEY,
            label VARCHAR
        );
    """)

    con.execute("""
        INSERT INTO _code_outcomes VALUES
        ('DE', 'Death'),
        ('HO', 'Hospitalization - Initial or Prolonged');
    """)

    con.execute("""
        INSERT INTO demo VALUES ('99901', 'CASE_MULTI', 1, '20200101', '20191201', '20191101', 55.0, 'Female', '2020Q1');
    """)
    con.execute("""
        INSERT INTO drug VALUES
        ('99901', 1, 'ASPIRIN', 'ASPIRIN', 'PS'),
        ('99901', 2, 'WARFARIN', 'WARFARIN', 'PS'),
        ('99901', 3, 'METFORMIN', 'METFORMIN', 'C');
    """)
    con.execute("""
        INSERT INTO reac VALUES
        ('99901', 'GASTROINTESTINAL HAEMORRHAGE'),
        ('99901', 'ANAEMIA'),
        ('99901', 'HYPOTENSION');
    """)
    con.execute("""
        INSERT INTO outc VALUES
        ('99901', 'HO'),
        ('99901', 'DE');
    """)

    con.execute(adapter.get_case_resolution_sql())
    for _view_name, view_sql in adapter.get_summary_views_sql().items():
        con.execute(view_sql)

    summary_rows = con.execute("""
        SELECT * FROM case_adverse_events_summary WHERE case_id = 'CASE_MULTI';
    """).fetchall()

    assert len(summary_rows) == 1

    row = con.execute("""
        SELECT
            case_id,
            primary_suspect_drugs,
            reaction_terms,
            reaction_count,
            outcome_codes,
            has_death,
            has_hospitalization,
            has_life_threatening
        FROM case_adverse_events_summary
        WHERE case_id = 'CASE_MULTI';
    """).fetchone()

    case_id, ps_drugs, reacs, reac_cnt, outc_codes, has_de, has_ho, has_lt = row
    assert case_id == "CASE_MULTI"
    assert set(ps_drugs) == {"ASPIRIN", "WARFARIN"}
    assert "METFORMIN" not in ps_drugs
    assert reac_cnt == 3
    assert set(reacs) == {"GASTROINTESTINAL HAEMORRHAGE", "ANAEMIA", "HYPOTENSION"}
    assert set(outc_codes) == {"HO", "DE"}
    assert has_de is True
    assert has_ho is True
    assert has_lt is False
    con.close()
