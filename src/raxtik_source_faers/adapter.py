"""FDA FAERS Source Adapter.

Extracts quarterly FDA FAERS ASCII zip archives into ephemeral staging files and loads
them into DuckDB canonical tables via signature-specific mappings (S1, S2, S3).
Implements the raxtik_etl.sources.protocol.SourceAdapter protocol.
"""

from __future__ import annotations

import hashlib
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Dict

import duckdb
from raxtik_etl.sources.protocol import SourceAdapter, SourceArtifact, SourceLoadResult
from rich.console import Console

from raxtik_source_faers.mappings.s1_legacy import (
    load_s1_demo,
    load_s1_drug,
    load_s1_indi,
    load_s1_outc,
    load_s1_reac,
    load_s1_rpsr,
    load_s1_ther,
)
from raxtik_source_faers.mappings.s2_migration import (
    load_s2_demo,
    load_s2_drug,
    load_s2_indi,
    load_s2_outc,
    load_s2_reac,
    load_s2_rpsr,
    load_s2_ther,
)
from raxtik_source_faers.mappings.s3_modern import (
    load_s3_demo,
    load_s3_drug,
    load_s3_indi,
    load_s3_outc,
    load_s3_reac,
    load_s3_rpsr,
    load_s3_ther,
)
from raxtik_source_faers.reference import (
    FDA_DECHALLENGE_REFERENCE,
    FDA_OCCUPATIONS_REFERENCE,
    FDA_OUTCOMES_REFERENCE,
    FDA_RECHALLENGE_REFERENCE,
    FDA_REPORT_SOURCES_REFERENCE,
    FDA_ROLES_REFERENCE,
)
from raxtik_source_faers.signatures.resolver import detect_archive_signature

console = Console()

TABLE_PREFIXES = ["DEMO", "DRUG", "REAC", "OUTC", "RPSR", "THER", "INDI"]


class FAERSAdapter(SourceAdapter):
    """Source adapter for FDA FAERS quarterly ASCII extracts."""

    source_name: str = "faers"

    def extract_and_load(
        self, con: duckdb.DuckDBPyConnection, artifact: SourceArtifact
    ) -> SourceLoadResult:
        """Extracts text files from ZIP into DuckDB staging tables and normalizes to canonical schemas."""
        zip_path = artifact.path
        if not zip_path.exists():
            raise FileNotFoundError(f"FAERS source archive not found at {zip_path}")

        # Derive release if not provided
        release = artifact.release
        if not release:
            match = re.search(r"(\d{4}q[1-4])", zip_path.name, re.IGNORECASE)
            release = match.group(1).upper() if match else "UNKNOWN"
        else:
            release = release.upper()

        zip_bytes = zip_path.read_bytes()
        zip_sha256 = hashlib.sha256(zip_bytes).hexdigest()

        with zipfile.ZipFile(zip_path, "r") as zf:
            signature_id = detect_archive_signature(zf, release)
            console.print(
                f"[cyan]Detected Schema Signature for {release}:[/cyan] [bold]{signature_id}[/bold]"
            )

            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)
                zf.extractall(tmp_path)

                extracted_files = [
                    f for f in tmp_path.rglob("*") if f.is_file() and f.suffix.lower() == ".txt"
                ]
                table_files: Dict[str, Path] = {}
                for prefix in TABLE_PREFIXES:
                    matches = [
                        f
                        for f in extracted_files
                        if re.search(rf"(?:^|[/\\]){prefix}[^/\\]*\.txt$", f.name, re.IGNORECASE)
                    ]
                    if matches:
                        table_files[prefix.lower()] = matches[0]

                if signature_id == "S1":
                    if "demo" in table_files:
                        load_s1_demo(con, table_files["demo"], release)
                    if "drug" in table_files:
                        load_s1_drug(con, table_files["drug"], release)
                    if "reac" in table_files:
                        load_s1_reac(con, table_files["reac"], release)
                    if "outc" in table_files:
                        load_s1_outc(con, table_files["outc"], release)
                    if "indi" in table_files:
                        load_s1_indi(con, table_files["indi"], release)
                    if "ther" in table_files:
                        load_s1_ther(con, table_files["ther"], release)
                    if "rpsr" in table_files:
                        load_s1_rpsr(con, table_files["rpsr"], release)

                elif signature_id == "S2":
                    if "demo" in table_files:
                        load_s2_demo(con, table_files["demo"], release)
                    if "drug" in table_files:
                        load_s2_drug(con, table_files["drug"], release)
                    if "reac" in table_files:
                        load_s2_reac(con, table_files["reac"], release)
                    if "outc" in table_files:
                        load_s2_outc(con, table_files["outc"], release)
                    if "indi" in table_files:
                        load_s2_indi(con, table_files["indi"], release)
                    if "ther" in table_files:
                        load_s2_ther(con, table_files["ther"], release)
                    if "rpsr" in table_files:
                        load_s2_rpsr(con, table_files["rpsr"], release)

                elif signature_id == "S3":
                    if "demo" in table_files:
                        load_s3_demo(con, table_files["demo"], release)
                    if "drug" in table_files:
                        load_s3_drug(con, table_files["drug"], release)
                    if "reac" in table_files:
                        load_s3_reac(con, table_files["reac"], release)
                    if "outc" in table_files:
                        load_s3_outc(con, table_files["outc"], release)
                    if "indi" in table_files:
                        load_s3_indi(con, table_files["indi"], release)
                    if "ther" in table_files:
                        load_s3_ther(con, table_files["ther"], release)
                    if "rpsr" in table_files:
                        load_s3_rpsr(con, table_files["rpsr"], release)

        row_counts = {}
        for tbl in ["demo", "drug", "reac", "outc", "indi", "ther", "rpsr"]:
            try:
                res = con.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()
                cnt = int(res[0]) if res is not None else 0
                row_counts[tbl] = cnt
            except Exception:
                row_counts[tbl] = 0

        source_files = [
            {
                "filename": zip_path.name,
                "byte_size": zip_path.stat().st_size,
                "sha256": zip_sha256,
                "table_type": "RAW_ARCHIVE_ZIP",
                "row_count": row_counts.get("demo", 0),
            }
        ]

        reference_tables = {
            "_code_outcomes": FDA_OUTCOMES_REFERENCE,
            "_code_roles": FDA_ROLES_REFERENCE,
            "_code_occupations": FDA_OCCUPATIONS_REFERENCE,
            "_code_report_sources": FDA_REPORT_SOURCES_REFERENCE,
            "_code_dechallenge": FDA_DECHALLENGE_REFERENCE,
            "_code_rechallenge": FDA_RECHALLENGE_REFERENCE,
        }

        return SourceLoadResult(
            source_name=self.source_name,
            release=release,
            signature_id=signature_id,
            source_files=source_files,
            reference_tables=reference_tables,
            row_counts=row_counts,
            metadata={
                "source_data_license": "US Government Work / Public Domain (17 U.S.C. § 105)"
            },
        )
