"""FDA FAERS Source Adapter.

Extracts quarterly FDA FAERS ASCII zip archives into ephemeral staging files and loads
them into DuckDB canonical tables via signature-specific mappings (S1, S2, S3).
Implements the raxtik_etl.sources.protocol.SourceAdapter protocol.
"""

from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Final, List, Set

import duckdb
from raxtik_etl.indexing.models import ResolutionPolicy
from raxtik_etl.packaging.builder import compute_sha256
from raxtik_etl.sources import (
    BaseSourceAdapter,
    SourceArtifact,
    SourceLoadResult,
    normalize_quarter,
)
from rich.console import Console

from raxtik_source_faers._version import __version__ as __source_version__
from raxtik_source_faers.constants import (
    CANONICAL_SCHEMA_VERSION,
    CANONICAL_TABLES,
    DEFAULT_RAW_CACHE_DIR,
    PROTOCOL_VERSION,
    SOURCE_NAME,
)
from raxtik_source_faers.fetcher import (
    download_quarterly_archive,
    find_local_faers_files,
)
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
    FDA_AGE_GROUPS_REFERENCE,
    FDA_AGE_UNITS_REFERENCE,
    FDA_CUMULATIVE_DOSE_UNITS_REFERENCE,
    FDA_DECHALLENGE_REFERENCE,
    FDA_DOSE_FREQUENCIES_REFERENCE,
    FDA_DRUG_NAME_SOURCES_REFERENCE,
    FDA_DURATION_UNITS_REFERENCE,
    FDA_OCCUPATIONS_REFERENCE,
    FDA_OUTCOMES_REFERENCE,
    FDA_RECHALLENGE_REFERENCE,
    FDA_REPORT_SOURCES_REFERENCE,
    FDA_REPORT_TYPES_REFERENCE,
    FDA_ROLES_REFERENCE,
    FDA_SEX_REFERENCE,
    FDA_WEIGHT_UNITS_REFERENCE,
    ICH_ISO_COUNTRIES_REFERENCE,
)
from raxtik_source_faers.signatures.resolver import detect_archive_signature

console = Console()

REQUIRED_TABLE_COLUMNS: Final[Dict[str, Dict[str, Set[str]]]] = {
    "S1": {
        "demo": {"isr", "case"},
        "drug": {"isr", "drugname"},
        "reac": {"isr", "pt"},
        "outc": {"isr", "outc_cod|outc_code"},
        "rpsr": {"isr"},
        "ther": {"isr"},
        "indi": {"isr"},
    },
    "S2": {
        "demo": {"primaryid", "caseid"},
        "drug": {"primaryid", "drugname"},
        "reac": {"primaryid", "pt"},
        "outc": {"primaryid", "outc_cod|outc_code"},
        "rpsr": {"primaryid"},
        "ther": {"primaryid"},
        "indi": {"primaryid"},
    },
    "S3": {
        "demo": {"primaryid", "caseid"},
        "drug": {"primaryid", "drugname"},
        "reac": {"primaryid", "pt"},
        "outc": {"primaryid", "outc_cod|outc_code"},
        "rpsr": {"primaryid"},
        "ther": {"primaryid"},
        "indi": {"primaryid"},
    },
}

# Mandatory tables required in every valid FDA FAERS/AERS quarterly archive.
# Other canonical tables (outc, indi, ther, rpsr) are optional if absent from an archive.
MANDATORY_TABLES: tuple[str, ...] = ("demo", "drug", "reac")

SIGNATURE_LOADERS = {
    "S1": {
        "demo": load_s1_demo,
        "drug": load_s1_drug,
        "reac": load_s1_reac,
        "outc": load_s1_outc,
        "indi": load_s1_indi,
        "ther": load_s1_ther,
        "rpsr": load_s1_rpsr,
    },
    "S2": {
        "demo": load_s2_demo,
        "drug": load_s2_drug,
        "reac": load_s2_reac,
        "outc": load_s2_outc,
        "indi": load_s2_indi,
        "ther": load_s2_ther,
        "rpsr": load_s2_rpsr,
    },
    "S3": {
        "demo": load_s3_demo,
        "drug": load_s3_drug,
        "reac": load_s3_reac,
        "outc": load_s3_outc,
        "indi": load_s3_indi,
        "ther": load_s3_ther,
        "rpsr": load_s3_rpsr,
    },
}


class FAERSAdapter(BaseSourceAdapter):
    """Source adapter for FDA FAERS quarterly ASCII extracts."""

    source_name: str = SOURCE_NAME
    source_version: str = __source_version__
    etl_version: str = __source_version__
    supported_schema_versions: List[str] = [CANONICAL_SCHEMA_VERSION]
    protocol_version: str = PROTOCOL_VERSION

    def fetch_archive(
        self,
        data_period: str,
        dest_dir: Path,
    ) -> Path:
        """Downloads official FDA FAERS/AERS ASCII zip archive for data_period.

        Args:
            data_period: Quarterly period identifier (e.g. '2004Q1').
            dest_dir: Destination folder to download archive into.

        Returns:
            Path to downloaded raw .zip archive.

        Raises:
            ValueError: If data_period format is invalid.
        """
        if not data_period:
            raise ValueError("Must provide data_period (e.g. '2004Q1')")
        if dest_dir is None:
            raise ValueError("Must provide dest_dir")

        try:
            canonical_period = normalize_quarter(data_period)
        except ValueError:
            raise ValueError(
                f"Invalid data_period format for FAERS: '{data_period}'. Expected format like '2004Q1'."
            )
        return download_quarterly_archive(data_period=canonical_period, dest_dir=dest_dir)

    def extract_and_load(
        self, con: duckdb.DuckDBPyConnection, artifact: SourceArtifact
    ) -> SourceLoadResult:
        """Extracts text files from ZIP into DuckDB staging tables and normalizes to canonical schemas.

        Args:
            con: Active DuckDB database connection.
            artifact: SourceArtifact describing path and data period.

        Returns:
            SourceLoadResult containing row counts, reference tables, and metadata.

        Raises:
            FileNotFoundError: If source zip does not exist.
        """
        zip_path = artifact.path
        # Derive data_period from artifact or archive filename
        raw_period = getattr(artifact, "data_period", None) or zip_path.name
        try:
            data_period = normalize_quarter(raw_period)
        except ValueError as err:
            raise ValueError(
                f"Cannot determine valid FAERS quarterly data_period from artifact or archive '{zip_path.name}'. "
                "A quarterly format like '2004Q1' is required."
            ) from err

        zip_sha256 = compute_sha256(zip_path)

        staging_dir = DEFAULT_RAW_CACHE_DIR.parent / "tmp"
        staging_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zf:
            signature_id = detect_archive_signature(zf, data_period)
            console.print(
                f"[cyan]Detected Schema Signature for {data_period}:[/cyan] [bold]{signature_id}[/bold]"
            )

            with tempfile.TemporaryDirectory(dir=staging_dir) as tmpdir:
                tmp_path = Path(tmpdir)
                zf.extractall(tmp_path)

                local_tables = find_local_faers_files(tmp_path)
                table_files: Dict[str, Path] = {
                    tbl: paths[0] for tbl, paths in local_tables.items() if paths
                }

                missing_mandatory = [t for t in MANDATORY_TABLES if t not in table_files]
                if missing_mandatory:
                    raise ValueError(
                        f"Incomplete FAERS archive '{zip_path.name}' for {data_period}: "
                        f"missing mandatory table(s) {missing_mandatory}. "
                        f"Found: {sorted(table_files.keys())}"
                    )

                loaders = SIGNATURE_LOADERS.get(signature_id, {})
                sig_required = REQUIRED_TABLE_COLUMNS.get(str(signature_id), {})
                for tbl_name, file_path in table_files.items():
                    req_cols = sig_required.get(tbl_name)
                    self.validate_extract_file(file_path, required_columns=req_cols, delimiter="$")

                    loader_fn = loaders.get(tbl_name)
                    if loader_fn:
                        loader_fn(con, file_path, data_period)

        row_counts = {}
        for tbl in CANONICAL_TABLES:
            try:
                res = con.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()
                cnt = int(res[0]) if res is not None else 0
                row_counts[tbl] = cnt
            except duckdb.CatalogException:
                console.print(
                    f"[dim yellow]Table '{tbl}' not present in DuckDB schema for {data_period}. Defaulting row count to 0.[/dim yellow]"
                )
                row_counts[tbl] = 0
            except Exception as err:
                raise RuntimeError(
                    f"Unexpected error reading row count for table '{tbl}' ({data_period}): {err}"
                ) from err

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
            "_code_report_types": FDA_REPORT_TYPES_REFERENCE,
            "_code_age_groups": FDA_AGE_GROUPS_REFERENCE,
            "_code_age_units": FDA_AGE_UNITS_REFERENCE,
            "_code_weight_units": FDA_WEIGHT_UNITS_REFERENCE,
            "_code_sex": FDA_SEX_REFERENCE,
            "_code_countries": ICH_ISO_COUNTRIES_REFERENCE,
            "_code_drug_name_sources": FDA_DRUG_NAME_SOURCES_REFERENCE,
            "_code_dose_frequencies": FDA_DOSE_FREQUENCIES_REFERENCE,
            "_code_duration_units": FDA_DURATION_UNITS_REFERENCE,
            "_code_cumulative_dose_units": FDA_CUMULATIVE_DOSE_UNITS_REFERENCE,
        }

        return SourceLoadResult(
            source_name=self.source_name,
            data_period=data_period,
            signature_id=signature_id,
            source_files=source_files,
            reference_tables=reference_tables,
            row_counts=row_counts,
            metadata={
                "source_data_license": "US Government Work / Public Domain (17 U.S.C. § 105)"
            },
        )

    def get_case_resolution_sql(self) -> str:
        """Returns SQL creating the deterministic deduplicated 'cases' view for FAERS.

        Returns:
            CREATE OR REPLACE VIEW SQL statement string.
        """
        return """
        CREATE OR REPLACE VIEW cases AS
        WITH ranked_reports AS (
            SELECT
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY case_id
                    ORDER BY
                        canonical_case_version DESC,
                        TRY_CAST(latest_regulatory_date AS BIGINT) DESC NULLS LAST,
                        TRY_CAST(manufacturer_date AS BIGINT) DESC NULLS LAST,
                        TRY_CAST(primary_id AS BIGINT) DESC
                ) AS _rn
            FROM demo
        )
        SELECT * EXCLUDE (_rn)
        FROM ranked_reports
        WHERE _rn = 1;
        """

    def get_case_lineage_sql(self) -> str:
        """Returns SQL creating the 'case_lineage' table tracking cross-quarter submission history for FAERS.

        Returns:
            CREATE OR REPLACE TABLE SQL statement string.
        """
        return """
        CREATE OR REPLACE TABLE case_lineage AS
        SELECT
            case_id,
            COUNT(DISTINCT primary_id) AS total_submissions_count,
            COUNT(DISTINCT _data_period) AS quarters_count,
            MIN(_data_period) AS first_data_period,
            MAX(_data_period) AS latest_data_period,
            MIN(TRY_CAST(latest_regulatory_date AS BIGINT)) AS first_regulatory_date,
            MAX(TRY_CAST(latest_regulatory_date AS BIGINT)) AS latest_regulatory_date,
            MIN(canonical_case_version) AS min_case_version,
            MAX(canonical_case_version) AS max_case_version,
            BOOL_OR(initial_or_followup_code = 'F') AS has_followup,
            (COUNT(DISTINCT _data_period) > 1) AS is_cross_quarter_case,
            FIRST(primary_id ORDER BY canonical_case_version ASC, TRY_CAST(latest_regulatory_date AS BIGINT) ASC, TRY_CAST(primary_id AS BIGINT) ASC) AS initial_primary_id,
            FIRST(primary_id ORDER BY canonical_case_version DESC, TRY_CAST(latest_regulatory_date AS BIGINT) DESC, TRY_CAST(primary_id AS BIGINT) DESC) AS latest_primary_id
        FROM demo
        GROUP BY case_id;
        """

    def get_summary_views_sql(self) -> Dict[str, str]:
        """Returns analytical summary views for FAERS with pre-aggregated non-fanout arrays.

        Returns:
            Mapping of view name to SQL CREATE OR REPLACE VIEW statement.
        """
        return {
            "case_adverse_events_summary": """
            CREATE OR REPLACE VIEW case_adverse_events_summary AS
            WITH drug_agg AS (
                SELECT
                    primary_id,
                    LIST(reported_drug_name ORDER BY TRY_CAST(drug_seq AS INTEGER) NULLS LAST, drug_seq) AS primary_suspect_drugs,
                    FIRST(reported_drug_name ORDER BY TRY_CAST(drug_seq AS INTEGER) NULLS LAST, drug_seq) AS primary_suspect_drug
                FROM drug
                WHERE role_code = 'PS'
                GROUP BY primary_id
            ),
            reac_agg AS (
                SELECT
                    primary_id,
                    LIST(reported_reaction_term ORDER BY reported_reaction_term) AS reaction_terms,
                    COUNT(DISTINCT reported_reaction_term) AS reaction_count
                FROM reac
                GROUP BY primary_id
            ),
            outc_agg AS (
                SELECT
                    o.primary_id,
                    LIST(o.outcome_code ORDER BY o.outcome_code) AS outcome_codes,
                    LIST(co.label ORDER BY o.outcome_code) AS outcome_labels,
                    BOOL_OR(o.outcome_code = 'DE') AS has_death,
                    BOOL_OR(o.outcome_code = 'LT') AS has_life_threatening,
                    BOOL_OR(o.outcome_code = 'HO') AS has_hospitalization
                FROM outc o
                LEFT JOIN _code_outcomes co ON o.outcome_code = co.code
                GROUP BY o.primary_id
            )
            SELECT
                c.case_id,
                c.primary_id,
                c.canonical_case_version,
                c.event_date,
                c.standard_age_years,
                c.standard_sex_label,
                c._data_period,
                COALESCE(d.primary_suspect_drugs, []) AS primary_suspect_drugs,
                d.primary_suspect_drug,
                COALESCE(r.reaction_terms, []) AS reaction_terms,
                COALESCE(r.reaction_count, 0) AS reaction_count,
                COALESCE(o.outcome_codes, []) AS outcome_codes,
                COALESCE(o.outcome_labels, []) AS outcome_labels,
                COALESCE(o.has_death, FALSE) AS has_death,
                COALESCE(o.has_life_threatening, FALSE) AS has_life_threatening,
                COALESCE(o.has_hospitalization, FALSE) AS has_hospitalization
            FROM cases c
            LEFT JOIN drug_agg d ON c.primary_id = d.primary_id
            LEFT JOIN reac_agg r ON c.primary_id = r.primary_id
            LEFT JOIN outc_agg o ON c.primary_id = o.primary_id;
            """
        }

    def get_resolution_policy(self) -> ResolutionPolicy:
        """Returns the FAERS-specific deterministic resolution policy for derived tier indexing.

        Explicitly declares FAERS canonical entity/record keys (`case_id`, `primary_id`),
        precedence columns (`canonical_case_version`, `latest_regulatory_date`,
        `manufacturer_date`), numeric `primary_id` tie-breaker, and all 6 FAERS child tables.
        """
        return ResolutionPolicy(
            entity_key="case_id",
            record_key="primary_id",
            version_column="canonical_case_version",
            regulatory_date_column="latest_regulatory_date",
            manufacturer_date_column="manufacturer_date",
            source_table="demo",
            child_tables=("drug", "reac", "outc", "indi", "ther", "rpsr"),
            numeric_record_key_tiebreaker=True,
            policy_version="faers-1.0.0",
        )
