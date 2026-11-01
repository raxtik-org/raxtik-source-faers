"""Tests for FAERS specialized client in raxtik-source-faers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import duckdb
import pytest
from raxtik_etl.packaging.builder import compute_sha256

from raxtik_source_faers import FAERS, build_package


@pytest.fixture
def fake_faers_package(tmp_path: Path) -> tuple[Path, str]:
    """Create a minimal mock FAERS duckdb package."""
    fake_pkg = tmp_path / "faers_2004Q1.duckdb"
    con = duckdb.connect(fake_pkg.as_posix())
    con.execute("CREATE TABLE demo (primary_id VARCHAR, case_id VARCHAR)")
    con.execute("CREATE TABLE cases (case_id VARCHAR, primary_id VARCHAR)")
    con.execute("INSERT INTO cases VALUES ('101', '101_1')")
    con.close()
    real_sha = compute_sha256(fake_pkg)
    return fake_pkg, real_sha


@pytest.mark.parametrize(
    ("sha_override", "expected_err"),
    [
        (None, None),
        ("invalid_sha", r"Checksum verification failed.*"),
    ],
)
def test_faers_client(
    tmp_path: Path,
    fake_faers_package: tuple[Path, str],
    sha_override: str | None,
    expected_err: str | None,
) -> None:
    """Verify FAERS client queries and parameterized checksum verification."""
    _, real_sha = fake_faers_package
    check_sha = sha_override or real_sha

    with FAERS.from_hf("2004Q1", package_dir=tmp_path) as faers:
        df = faers.cases()
        assert len(df) == 1
        assert df["case_id"][0] == "101"
        if expected_err:
            with pytest.raises(ValueError, match=expected_err):
                faers.verify_checksum(check_sha)
        else:
            assert faers.verify_checksum(check_sha) is True


@pytest.mark.parametrize(
    ("caller", "arg", "match_pattern"),
    [
        (FAERS, "", r"Must provide data_period.*"),
        (FAERS.from_hf, "", r"Must provide data_period.*"),
        (
            lambda p: build_package(data_period=p),
            "invalid_rel",
            r"Invalid (?:quarterly|FAERS).*format.*",
        ),
        (
            lambda p: build_package(data_period=p),
            "",
            r"Invalid (?:quarterly|FAERS).*format.*",
        ),
    ],
)
def test_client_invalid_data_period(
    caller: Callable[[Any], Any], arg: str, match_pattern: str
) -> None:
    """Verify fail-fast validation when invalid or empty data_period is provided."""
    with pytest.raises(ValueError, match=match_pattern):
        caller(arg)


@pytest.mark.parametrize(
    ("source_arg", "hf_repo_arg", "expected_source", "expected_repo"),
    [
        (None, None, "faers", "raxtik-org/faers-safety-database"),
        ("faers", None, "faers", "raxtik-org/faers-safety-database"),
        ("vaers", None, "vaers", "raxtik-org/vaers-safety-database"),
        ("my_source", "custom/custom-repo", "my_source", "custom/custom-repo"),
    ],
)
def test_client_source_and_hf_repo_resolution(
    tmp_path: Path,
    source_arg: str | None,
    hf_repo_arg: str | None,
    expected_source: str,
    expected_repo: str,
) -> None:
    """Verify that source is honored and hf_repo is created dynamically based on source in BaseDataset."""
    src_name = source_arg or "faers"
    pkg = tmp_path / f"{src_name}_2004Q1.duckdb"
    con = duckdb.connect(pkg.as_posix())
    con.execute("CREATE TABLE demo (primary_id VARCHAR, case_id VARCHAR)")
    con.close()

    kwargs: dict[str, Any] = {"package_dir": tmp_path}
    if source_arg is not None:
        kwargs["source"] = source_arg
    if hf_repo_arg is not None:
        kwargs["hf_repo"] = hf_repo_arg

    client = FAERS("2004Q1", **kwargs)
    assert client.source == expected_source
    assert client.hf_repo == expected_repo
    client.close()
