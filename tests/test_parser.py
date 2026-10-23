"""Unit tests for FAERS $-delimited ASCII parser."""

from __future__ import annotations

from pathlib import Path

from raxtik_source_faers.parser import clean_field_name, detect_table_type, parse_faers_ascii_file


def test_detect_table_type() -> None:
    assert detect_table_type("DEMO04Q1.txt") == "demo"
    assert detect_table_type("drug24q1.txt") == "drug"
    assert detect_table_type("/path/to/REAC12Q4.TXT") == "reac"
    assert detect_table_type("OUTC20Q3.txt") == "outc"
    assert detect_table_type("INDI05Q2.txt") == "indi"
    assert detect_table_type("THER14Q1.txt") == "ther"
    assert detect_table_type("RPSR19Q4.txt") == "rpsr"
    assert detect_table_type("unknown_file.txt") is None


def test_clean_field_name() -> None:
    assert clean_field_name("PRIMARYID") == "primaryid"
    assert clean_field_name("  CASE_ID  ") == "case_id"
    assert clean_field_name("FOLL-SEQ#") == "foll_seq"
    assert clean_field_name("__WT_COD__") == "wt_cod"


def test_parse_faers_ascii_file(tmp_path: Path) -> None:
    sample_file = tmp_path / "DEMO24Q1.txt"
    content = "\n".join(
        [
            "PRIMARYID$CASEID$SEX$AGE$AGE_COD",
            "10000001$10000001$F$45$YR",
            "10000002$10000002$M$62$YR",
            "",
        ]
    )
    sample_file.write_text(content)
    records = list(parse_faers_ascii_file(sample_file))
    assert len(records) == 2
    assert records[0]["primaryid"] == "10000001"
    assert records[0]["sex"] == "F"
    assert records[0]["_table_type"] == "demo"
    assert records[1]["primaryid"] == "10000002"
    assert records[1]["sex"] == "M"
