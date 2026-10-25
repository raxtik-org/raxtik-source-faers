"""Tests for FAERS specialized client in raxtik-source-faers."""

from pathlib import Path

import duckdb
import pytest
from raxtik_etl.packaging.builder import compute_sha256

from raxtik_source_faers import FAERS, build_package


def test_faers_client(tmp_path: Path):
    fake_pkg = tmp_path / "faers_2004Q1.duckdb"
    con = duckdb.connect(fake_pkg.as_posix())
    con.execute("CREATE TABLE demo (primary_id VARCHAR, case_id VARCHAR)")
    con.execute("CREATE TABLE cases (case_id VARCHAR, primary_id VARCHAR)")
    con.execute("INSERT INTO cases VALUES ('101', '101_1')")
    con.close()

    real_sha = compute_sha256(fake_pkg)

    with FAERS.from_hf("2004Q1", package_dir=tmp_path, expected_sha256=real_sha) as faers:
        df = faers.cases()
        assert len(df) == 1
        assert df["case_id"][0] == "101"
        assert faers.verify_checksum(real_sha) is True

    # Bad sha raises ValueError
    with pytest.raises(ValueError, match="Checksum verification failed"):
        FAERS.from_hf("2004Q1", package_dir=tmp_path, expected_sha256="invalid_sha")


def test_build_package_invalid_release():
    with pytest.raises(ValueError, match="Invalid FAERS release format"):
        build_package(release="invalid_rel")
