"""Signature S1 (Legacy AERS: 2004Q1 - 2012Q3) Canonical Mapping.

Maps raw AERS text files (ISR, CASE, FOLL_SEQ, GNDR_COD) to the canonical schema.
"""

from __future__ import annotations

from pathlib import Path

import duckdb
from raxtik_etl.transformations.normalization import (
    get_age_unit_label_sql,
    get_date_precision_sql,
    get_dechallenge_label_sql,
    get_drug_name_source_label_sql,
    get_drug_role_label_sql,
    get_duration_unit_label_sql,
    get_initial_or_followup_label_sql,
    get_outcome_is_serious_sql,
    get_outcome_label_sql,
    get_rechallenge_label_sql,
    get_report_source_label_sql,
    get_report_type_label_sql,
    get_reporter_occupation_label_sql,
    get_standard_age_sql,
    get_standard_date_sql,
    get_standard_duration_days_sql,
    get_standard_sex_label_sql,
    get_standard_weight_sql,
    get_weight_unit_label_sql,
)


def load_s1_demo(con: duckdb.DuckDBPyConnection, file_path: Path, data_period: str):
    """Loads S1 DEMO file into canonical demo table."""
    age_sql = get_standard_age_sql("AGE", "AGE_COD")
    wt_sql = get_standard_weight_sql("WT", "WT_COD")
    sex_label_sql = get_standard_sex_label_sql("GNDR_COD")
    if_label_sql = get_initial_or_followup_label_sql("I_F_COD")
    occp_label_sql = get_reporter_occupation_label_sql("OCCP_COD")
    rept_label_sql = get_report_type_label_sql("REPT_COD")
    age_unit_lbl_sql = get_age_unit_label_sql("AGE_COD")
    wt_unit_lbl_sql = get_weight_unit_label_sql("WT_COD")

    std_event_dt_sql = get_standard_date_sql("EVENT_DT")
    event_dt_prec_sql = get_date_precision_sql("EVENT_DT")

    std_mfr_dt_sql = get_standard_date_sql("MFR_DT")
    mfr_dt_prec_sql = get_date_precision_sql("MFR_DT")

    std_fda_dt_sql = get_standard_date_sql("FDA_DT")
    fda_dt_prec_sql = get_date_precision_sql("FDA_DT")

    std_rept_dt_sql = get_standard_date_sql("REPT_DT")
    rept_dt_prec_sql = get_date_precision_sql("REPT_DT")

    std_death_dt_sql = get_standard_date_sql("DEATH_DT")
    death_dt_prec_sql = get_date_precision_sql("DEATH_DT")

    con.execute(f"""
        CREATE OR REPLACE TABLE demo AS
        SELECT
            CAST(ISR AS VARCHAR) AS primary_id,
            CAST(COALESCE("CASE", ISR) AS VARCHAR) AS case_id,
            CAST(NULL AS INTEGER) AS source_case_version,
            CAST(COALESCE(TRY_CAST(FOLL_SEQ AS INTEGER) + 1, 1) AS INTEGER) AS canonical_case_version,
            'DERIVED_FROM_FOLL_SEQ' AS case_version_source,
            CAST(FOLL_SEQ AS VARCHAR) AS foll_seq,
            CAST(I_F_COD AS VARCHAR) AS initial_or_followup_code,
            {if_label_sql} AS initial_or_followup_label,
            CAST(EVENT_DT AS VARCHAR) AS event_date,
            {std_event_dt_sql} AS standard_event_date,
            {event_dt_prec_sql} AS event_date_precision,
            CAST(MFR_DT AS VARCHAR) AS manufacturer_date,
            {std_mfr_dt_sql} AS standard_manufacturer_date,
            {mfr_dt_prec_sql} AS manufacturer_date_precision,
            CAST(NULL AS VARCHAR) AS initial_regulatory_date,
            CAST(NULL AS DATE) AS standard_initial_regulatory_date,
            CAST(NULL AS VARCHAR) AS initial_regulatory_date_precision,
            CAST(FDA_DT AS VARCHAR) AS latest_regulatory_date,
            {std_fda_dt_sql} AS standard_latest_regulatory_date,
            {fda_dt_prec_sql} AS latest_regulatory_date_precision,
            CAST(REPT_DT AS VARCHAR) AS report_date,
            {std_rept_dt_sql} AS standard_report_date,
            {rept_dt_prec_sql} AS report_date_precision,
            CAST(DEATH_DT AS VARCHAR) AS death_date,
            {std_death_dt_sql} AS standard_death_date,
            {death_dt_prec_sql} AS death_date_precision,
            CAST(CONFID AS VARCHAR) AS confidentiality_flag,
            CAST(REPT_COD AS VARCHAR) AS report_type_code,
            {rept_label_sql} AS report_type_label,
            CASE WHEN UPPER(TRIM(REPT_COD)) = 'EXP' THEN 'Y' ELSE 'N' END AS expedited_flag,
            CAST(E_SUB AS VARCHAR) AS electronic_submission_flag,
            CAST(MFR_NUM AS VARCHAR) AS manufacturer_control_number,
            CAST(MFR_SNDR AS VARCHAR) AS manufacturer_name,
            CAST(NULL AS VARCHAR) AS auth_num,
            CAST(NULL AS VARCHAR) AS lit_ref,
            CAST(TO_MFR AS VARCHAR) AS to_mfr,
            CAST(NULL AS VARCHAR) AS sender_type_code,
            CAST(NULL AS VARCHAR) AS sender_type_label,
            TRY_CAST(AGE AS DOUBLE) AS reported_age,
            CAST(AGE_COD AS VARCHAR) AS reported_age_code,
            {age_unit_lbl_sql} AS reported_age_unit_label,
            CAST(NULL AS VARCHAR) AS age_group_code,
            CAST(NULL AS VARCHAR) AS age_group_label,
            CAST(GNDR_COD AS VARCHAR) AS reported_sex_code,
            TRY_CAST(WT AS DOUBLE) AS reported_weight,
            CAST(WT_COD AS VARCHAR) AS reported_weight_code,
            {wt_unit_lbl_sql} AS reported_weight_unit_label,
            CAST(OCCP_COD AS VARCHAR) AS reporter_occupation_code,
            {occp_label_sql} AS reporter_occupation_label,
            CAST(NULL AS VARCHAR) AS reporter_country,
            CAST(NULL AS VARCHAR) AS occurrence_country,
            {age_sql} AS standard_age_years,
            {sex_label_sql} AS standard_sex_label,
            {wt_sql} AS standard_weight_kg,
            'FDA_FAERS_ASCII' AS _source_system,
            '{data_period}' AS _data_period,
            '{file_path.name}' AS _source_file,
            'S1' AS _source_signature_id,
            CURRENT_TIMESTAMP AS _ingested_at
        FROM read_csv('{file_path.as_posix()}', delim='$', header=True, all_varchar=True, quote='', escape='', ignore_errors=true, null_padding=true);
    """)


def load_s1_drug(con: duckdb.DuckDBPyConnection, file_path: Path, data_period: str):
    """Loads S1 DRUG file into canonical drug table."""
    role_label_sql = get_drug_role_label_sql("d.ROLE_COD")
    val_vbm_lbl_sql = get_drug_name_source_label_sql("d.VAL_VBM")
    dechal_lbl_sql = get_dechallenge_label_sql("d.DECHAL")
    rechal_lbl_sql = get_rechallenge_label_sql("d.RECHAL")
    std_exp_dt_sql = get_standard_date_sql("d.EXP_DT")
    exp_dt_prec_sql = get_date_precision_sql("d.EXP_DT")
    con.execute(f"""
        CREATE OR REPLACE TABLE drug AS
        SELECT
            CAST(d.ISR AS VARCHAR) AS primary_id,
            CAST(dm.case_id AS VARCHAR) AS case_id,
            COALESCE(NULLIF(TRIM(CAST(d.DRUG_SEQ AS VARCHAR)), ''), '1') AS drug_seq,
            CAST(d.DRUGNAME AS VARCHAR) AS reported_drug_name,
            CAST(NULL AS VARCHAR) AS reported_active_ingredient,
            CAST(d.VAL_VBM AS VARCHAR) AS reported_validation_code,
            {val_vbm_lbl_sql} AS reported_validation_label,
            CAST(d.ROLE_COD AS VARCHAR) AS role_code,
            {role_label_sql} AS role_label,
            CAST(d.ROUTE AS VARCHAR) AS route,
            CAST(d.DOSE_VBM AS VARCHAR) AS reported_dose_verbatim,
            CAST(NULL AS DOUBLE) AS dose_amount,
            CAST(NULL AS VARCHAR) AS dose_unit,
            CAST(NULL AS VARCHAR) AS dose_form,
            CAST(NULL AS VARCHAR) AS dose_frequency,
            CAST(NULL AS VARCHAR) AS dose_frequency_label,
            CAST(NULL AS VARCHAR) AS cumulative_dose_amount,
            CAST(NULL AS VARCHAR) AS cumulative_dose_unit,
            CAST(NULL AS VARCHAR) AS cumulative_dose_unit_label,
            CAST(d.DECHAL AS VARCHAR) AS dechallenge_code,
            {dechal_lbl_sql} AS dechallenge_label,
            CAST(d.RECHAL AS VARCHAR) AS rechallenge_code,
            {rechal_lbl_sql} AS rechallenge_label,
            CAST(d.LOT_NUM AS VARCHAR) AS lot_number,
            CAST(d.EXP_DT AS VARCHAR) AS expiration_date,
            {std_exp_dt_sql} AS standard_expiration_date,
            {exp_dt_prec_sql} AS expiration_date_precision,
            CAST(d.NDA_NUM AS VARCHAR) AS regulatory_auth_num,
            TRIM(UPPER(CAST(d.DRUGNAME AS VARCHAR))) AS structural_clean_drug_name,
            CAST(NULL AS VARCHAR) AS standard_concept_name,
            CAST(NULL AS VARCHAR) AS standard_concept_source,
            CAST(NULL AS VARCHAR) AS rxcui,
            'NOT_ATTEMPTED' AS derivation_status,
            'FDA_FAERS_ASCII' AS _source_system,
            '{data_period}' AS _data_period,
            '{file_path.name}' AS _source_file,
            'S1' AS _source_signature_id,
            CURRENT_TIMESTAMP AS _ingested_at
        FROM read_csv('{file_path.as_posix()}', delim='$', header=True, all_varchar=True, quote='', escape='', ignore_errors=true, null_padding=true) d
        LEFT JOIN demo dm ON CAST(d.ISR AS VARCHAR) = dm.primary_id;
    """)


def load_s1_reac(con: duckdb.DuckDBPyConnection, file_path: Path, data_period: str):
    """Loads S1 REAC file into canonical reac table."""
    con.execute(f"""
        CREATE OR REPLACE TABLE reac AS
        SELECT
            CAST(r.ISR AS VARCHAR) AS primary_id,
            CAST(dm.case_id AS VARCHAR) AS case_id,
            CAST(r.PT AS VARCHAR) AS reported_reaction_term,
            ROW_NUMBER() OVER (PARTITION BY r.ISR) AS reaction_seq,
            CAST(NULL AS VARCHAR) AS drug_reaction_action,
            'FDA_FAERS_ASCII' AS _source_system,
            '{data_period}' AS _data_period,
            '{file_path.name}' AS _source_file,
            'S1' AS _source_signature_id,
            CURRENT_TIMESTAMP AS _ingested_at
        FROM read_csv('{file_path.as_posix()}', delim='$', header=True, all_varchar=True, quote='', escape='', ignore_errors=true, null_padding=true) r
        LEFT JOIN demo dm ON CAST(r.ISR AS VARCHAR) = dm.primary_id;
    """)


def load_s1_outc(con: duckdb.DuckDBPyConnection, file_path: Path, data_period: str):
    """Loads S1 OUTC file into canonical outc table."""
    outc_lbl_sql = get_outcome_label_sql("o.OUTC_COD")
    serious_sql = get_outcome_is_serious_sql("o.OUTC_COD")
    con.execute(f"""
        CREATE OR REPLACE TABLE outc AS
        SELECT
            CAST(o.ISR AS VARCHAR) AS primary_id,
            CAST(dm.case_id AS VARCHAR) AS case_id,
            CAST(o.OUTC_COD AS VARCHAR) AS outcome_code,
            {outc_lbl_sql} AS outcome_label,
            {serious_sql} AS is_serious,
            'FDA_FAERS_ASCII' AS _source_system,
            '{data_period}' AS _data_period,
            '{file_path.name}' AS _source_file,
            'S1' AS _source_signature_id,
            CURRENT_TIMESTAMP AS _ingested_at
        FROM read_csv('{file_path.as_posix()}', delim='$', header=True, all_varchar=True, quote='', escape='', ignore_errors=true, null_padding=true) o
        LEFT JOIN demo dm ON CAST(o.ISR AS VARCHAR) = dm.primary_id;
    """)


def load_s1_indi(con: duckdb.DuckDBPyConnection, file_path: Path, data_period: str):
    """Loads S1 INDI file into canonical indi table."""
    con.execute(f"""
        CREATE OR REPLACE TABLE indi AS
        SELECT
            CAST(i.ISR AS VARCHAR) AS primary_id,
            CAST(dm.case_id AS VARCHAR) AS case_id,
            COALESCE(NULLIF(TRIM(CAST(i.DRUG_SEQ AS VARCHAR)), ''), '1') AS indication_drug_seq,
            CAST(i.INDI_PT AS VARCHAR) AS reported_indication_term,
            'FDA_FAERS_ASCII' AS _source_system,
            '{data_period}' AS _data_period,
            '{file_path.name}' AS _source_file,
            'S1' AS _source_signature_id,
            CURRENT_TIMESTAMP AS _ingested_at
        FROM read_csv('{file_path.as_posix()}', delim='$', header=True, all_varchar=True, quote='', escape='', ignore_errors=true, null_padding=true) i
        LEFT JOIN demo dm ON CAST(i.ISR AS VARCHAR) = dm.primary_id;
    """)


def load_s1_ther(con: duckdb.DuckDBPyConnection, file_path: Path, data_period: str):
    """Loads S1 THER file into canonical ther table."""
    dur_sql = get_standard_duration_days_sql("t.DUR", "t.DUR_COD")
    dur_lbl_sql = get_duration_unit_label_sql("t.DUR_COD")
    std_start_dt_sql = get_standard_date_sql("t.START_DT")
    start_dt_prec_sql = get_date_precision_sql("t.START_DT")
    std_end_dt_sql = get_standard_date_sql("t.END_DT")
    end_dt_prec_sql = get_date_precision_sql("t.END_DT")
    con.execute(f"""
        CREATE OR REPLACE TABLE ther AS
        SELECT
            CAST(t.ISR AS VARCHAR) AS primary_id,
            CAST(dm.case_id AS VARCHAR) AS case_id,
            COALESCE(NULLIF(TRIM(CAST(t.DRUG_SEQ AS VARCHAR)), ''), '1') AS therapy_drug_seq,
            CAST(t.START_DT AS VARCHAR) AS start_date,
            {std_start_dt_sql} AS standard_start_date,
            {start_dt_prec_sql} AS start_date_precision,
            CAST(t.END_DT AS VARCHAR) AS end_date,
            {std_end_dt_sql} AS standard_end_date,
            {end_dt_prec_sql} AS end_date_precision,
            TRY_CAST(t.DUR AS DOUBLE) AS reported_duration,
            CAST(t.DUR_COD AS VARCHAR) AS reported_duration_code,
            {dur_lbl_sql} AS reported_duration_label,
            {dur_sql} AS standard_duration_days,
            'FDA_FAERS_ASCII' AS _source_system,
            '{data_period}' AS _data_period,
            '{file_path.name}' AS _source_file,
            'S1' AS _source_signature_id,
            CURRENT_TIMESTAMP AS _ingested_at
        FROM read_csv('{file_path.as_posix()}', delim='$', header=True, all_varchar=True, quote='', escape='', ignore_errors=true, null_padding=true) t
        LEFT JOIN demo dm ON CAST(t.ISR AS VARCHAR) = dm.primary_id;
    """)


def load_s1_rpsr(con: duckdb.DuckDBPyConnection, file_path: Path, data_period: str):
    """Loads S1 RPSR file into canonical rpsr table."""
    rpsr_lbl_sql = get_report_source_label_sql("r.RPSR_COD")
    con.execute(f"""
        CREATE OR REPLACE TABLE rpsr AS
        SELECT
            CAST(r.ISR AS VARCHAR) AS primary_id,
            CAST(dm.case_id AS VARCHAR) AS case_id,
            CAST(r.RPSR_COD AS VARCHAR) AS report_source_code,
            {rpsr_lbl_sql} AS report_source_label,
            'FDA_FAERS_ASCII' AS _source_system,
            '{data_period}' AS _data_period,
            '{file_path.name}' AS _source_file,
            'S1' AS _source_signature_id,
            CURRENT_TIMESTAMP AS _ingested_at
        FROM read_csv('{file_path.as_posix()}', delim='$', header=True, all_varchar=True, quote='', escape='', ignore_errors=true, null_padding=true) r
        LEFT JOIN demo dm ON CAST(r.ISR AS VARCHAR) = dm.primary_id;
    """)
