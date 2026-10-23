"""Integration test for FAERSAdapter extracting into DuckDB."""

import os
from pathlib import Path

import duckdb
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

    artifact = SourceArtifact(path=CACHE_2004Q1, release="2004Q1")
    result = adapter.extract_and_load(con, artifact)

    assert result.source_name == "faers"
    assert result.release == "2004Q1"
    assert result.signature_id == "S1"
    assert result.row_counts["demo"] == 65902
    assert result.row_counts["drug"] == 235361
    assert result.row_counts["reac"] == 264410
    assert result.row_counts["outc"] == 57592
    assert result.row_counts["indi"] == 78639
    assert result.row_counts["ther"] == 84964
    assert result.row_counts["rpsr"] == 78306

    # Verify reference tables delivered
    assert "_code_outcomes" in result.reference_tables
    assert len(result.reference_tables["_code_outcomes"]) == 7
    assert "_code_roles" in result.reference_tables
    assert "_code_occupations" in result.reference_tables
    assert "_code_report_sources" in result.reference_tables
    assert "_code_dechallenge" in result.reference_tables
    assert "_code_rechallenge" in result.reference_tables

    con.close()
