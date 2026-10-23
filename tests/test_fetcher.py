"""Unit tests for FAERS archive fetcher and file discovery."""

from __future__ import annotations

from pathlib import Path

import pytest

from raxtik_source_faers.fetcher import download_quarterly_archive, find_local_faers_files


def test_find_local_faers_files(tmp_path: Path) -> None:
    sub = tmp_path / "ascii"
    sub.mkdir()
    (sub / "DEMO04Q1.txt").write_text("header\n")
    (sub / "DRUG04Q1.txt").write_text("header\n")
    (sub / "REAC04Q1.txt").write_text("header\n")
    (sub / "random.txt").write_text("ignored\n")

    res = find_local_faers_files(tmp_path)
    assert "demo" in res
    assert len(res["demo"]) == 1
    assert "drug" in res
    assert "reac" in res
    assert "random" not in res


def test_download_quarterly_archive_validation() -> None:
    with pytest.raises(ValueError, match="Invalid quarter: 5"):
        download_quarterly_archive(2024, 5)

    with pytest.raises(ValueError, match="Invalid quarter: 0"):
        download_quarterly_archive(2024, 0)


def test_download_quarterly_archive_skip_existing(tmp_path: Path) -> None:
    existing_zip = tmp_path / "faers_ascii_2024q1.zip"
    existing_zip.write_bytes(b"PK\x05\x06" + b"\x00" * 18)

    returned = download_quarterly_archive(2024, 1, dest_dir=tmp_path, overwrite=False)
    assert returned == existing_zip
