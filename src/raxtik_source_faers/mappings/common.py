"""Common table loading routines shared across FAERS schema signatures."""

from __future__ import annotations

from pathlib import Path

import duckdb
from raxtik_etl.transformations.normalization import get_standard_duration_days_sql


def load_standard_indi(
    con: duckdb.DuckDBPyConnection,
    file_path: Path,
    data_period: str,
    signature_id: str,
) -> None:
    """Loads standardized INDI file into canonical indi table."""
    con.execute(f"""
        CREATE OR REPLACE TABLE indi AS
        SELECT
            CAST(primaryid AS VARCHAR) AS primary_id,
            CAST(caseid AS VARCHAR) AS case_id,
            COALESCE(TRY_CAST(indi_drug_seq AS INTEGER), 1) AS indication_drug_seq,
            CAST(indi_pt AS VARCHAR) AS reported_indication_term,
            'FDA_FAERS_ASCII' AS _source_system,
            '{data_period}' AS _data_period,
            '{file_path.name}' AS _source_file,
            '{signature_id}' AS _source_signature_id,
            CURRENT_TIMESTAMP AS _ingested_at
        FROM read_csv('{file_path.as_posix()}', delim='$', header=True, all_varchar=True, quote='', escape='', ignore_errors=true, null_padding=true);
    """)


def load_standard_ther(
    con: duckdb.DuckDBPyConnection,
    file_path: Path,
    data_period: str,
    signature_id: str,
) -> None:
    """Loads standardized THER file into canonical ther table."""
    dur_sql = get_standard_duration_days_sql("dur", "dur_cod")
    con.execute(f"""
        CREATE OR REPLACE TABLE ther AS
        SELECT
            CAST(primaryid AS VARCHAR) AS primary_id,
            CAST(caseid AS VARCHAR) AS case_id,
            COALESCE(TRY_CAST(dsg_drug_seq AS INTEGER), 1) AS therapy_drug_seq,
            CAST(start_dt AS VARCHAR) AS start_date,
            CAST(end_dt AS VARCHAR) AS end_date,
            TRY_CAST(dur AS DOUBLE) AS reported_duration,
            CAST(dur_cod AS VARCHAR) AS reported_duration_code,
            {dur_sql} AS standard_duration_days,
            'FDA_FAERS_ASCII' AS _source_system,
            '{data_period}' AS _data_period,
            '{file_path.name}' AS _source_file,
            '{signature_id}' AS _source_signature_id,
            CURRENT_TIMESTAMP AS _ingested_at
        FROM read_csv('{file_path.as_posix()}', delim='$', header=True, all_varchar=True, quote='', escape='', ignore_errors=true, null_padding=true);
    """)


def load_standard_rpsr(
    con: duckdb.DuckDBPyConnection,
    file_path: Path,
    data_period: str,
    signature_id: str,
) -> None:
    """Loads standardized RPSR file into canonical rpsr table."""
    con.execute(f"""
        CREATE OR REPLACE TABLE rpsr AS
        SELECT
            CAST(primaryid AS VARCHAR) AS primary_id,
            CAST(caseid AS VARCHAR) AS case_id,
            CAST(rpsr_cod AS VARCHAR) AS report_source_code,
            'FDA_FAERS_ASCII' AS _source_system,
            '{data_period}' AS _data_period,
            '{file_path.name}' AS _source_file,
            '{signature_id}' AS _source_signature_id,
            CURRENT_TIMESTAMP AS _ingested_at
        FROM read_csv('{file_path.as_posix()}', delim='$', header=True, all_varchar=True, quote='', escape='', ignore_errors=true, null_padding=true);
    """)
