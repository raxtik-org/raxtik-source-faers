"""Signature S3 (Modern FAERS & AEMS: 2014Q3 - 2026Q2+) Canonical Mapping.

Maps raw S3 modern text files to canonical schema:
- DEMO: primaryid, caseid, caseversion, i_f_code, event_dt, mfr_dt, init_fda_dt, fda_dt,
        rept_cod, auth_num, mfr_num, mfr_sndr, lit_ref, age, age_cod, age_grp, sex, e_sub,
        wt, wt_cod, rept_dt, to_mfr, occp_cod, reporter_country, occr_country
- DRUG: primaryid, caseid, drug_seq, role_cod, drugname, prod_ai, val_vbm, route, dose_vbm,
        cum_dose_chr, cum_dose_unit, dechal, rechal, lot_num, exp_dt, nda_num, dose_amt,
        dose_unit, dose_form, dose_freq
- REAC: primaryid, caseid, pt, drug_rec_act
- OUTC: primaryid, caseid, outc_cod
- INDI: primaryid, caseid, indi_drug_seq, indi_pt
- THER: primaryid, caseid, dsg_drug_seq, start_dt, end_dt, dur, dur_cod
- RPSR: primaryid, caseid, rpsr_cod

Critical S3 Normalization Rules:
1. Centralized age/weight normalization using normalization.py (converting MON/WK/DY/HR and LBS/GMS)
2. No premature drug normalization: standard_concept_name = NULL, derivation_status = 'NOT_ATTEMPTED'
3. Preserves raw reported codes without hard-coding labels (labels resolved in _code_* dimensions)
"""

from __future__ import annotations

from pathlib import Path

import duckdb
from raxtik_etl.transformations.normalization import (
    get_date_precision_sql,
    get_dechallenge_label_sql,
    get_drug_role_label_sql,
    get_initial_or_followup_label_sql,
    get_outcome_is_serious_sql,
    get_outcome_label_sql,
    get_rechallenge_label_sql,
    get_report_type_label_sql,
    get_reporter_occupation_label_sql,
    get_standard_age_sql,
    get_standard_date_sql,
    get_standard_sex_label_sql,
    get_standard_weight_sql,
)

from raxtik_source_faers.mappings.common import (
    load_standard_indi,
    load_standard_rpsr,
    load_standard_ther,
)


def load_s3_demo(con: duckdb.DuckDBPyConnection, file_path: Path, data_period: str):
    """Loads S3 DEMO file into canonical demo table."""
    age_sql = get_standard_age_sql("age", "age_cod")
    wt_sql = get_standard_weight_sql("wt", "wt_cod")
    sex_label_sql = get_standard_sex_label_sql("sex")
    if_label_sql = get_initial_or_followup_label_sql("i_f_code")
    occp_label_sql = get_reporter_occupation_label_sql("occp_cod")
    rept_label_sql = get_report_type_label_sql("rept_cod")

    std_event_dt_sql = get_standard_date_sql("event_dt")
    event_dt_prec_sql = get_date_precision_sql("event_dt")

    std_mfr_dt_sql = get_standard_date_sql("mfr_dt")
    mfr_dt_prec_sql = get_date_precision_sql("mfr_dt")

    std_init_fda_dt_sql = get_standard_date_sql("init_fda_dt")
    init_fda_dt_prec_sql = get_date_precision_sql("init_fda_dt")

    std_fda_dt_sql = get_standard_date_sql("fda_dt")
    fda_dt_prec_sql = get_date_precision_sql("fda_dt")

    std_rept_dt_sql = get_standard_date_sql("rept_dt")
    rept_dt_prec_sql = get_date_precision_sql("rept_dt")

    con.execute(f"""
        CREATE OR REPLACE TABLE demo AS
        SELECT
            CAST(primaryid AS VARCHAR) AS primary_id,
            CAST(caseid AS VARCHAR) AS case_id,
            TRY_CAST(caseversion AS INTEGER) AS source_case_version,
            COALESCE(TRY_CAST(caseversion AS INTEGER), 1) AS canonical_case_version,
            'FDA_REPORTED' AS case_version_source,
            CAST(NULL AS VARCHAR) AS foll_seq,
            CAST(i_f_code AS VARCHAR) AS initial_or_followup_code,
            {if_label_sql} AS initial_or_followup_label,
            CAST(event_dt AS VARCHAR) AS event_date,
            {std_event_dt_sql} AS standard_event_date,
            {event_dt_prec_sql} AS event_date_precision,
            CAST(mfr_dt AS VARCHAR) AS manufacturer_date,
            {std_mfr_dt_sql} AS standard_manufacturer_date,
            {mfr_dt_prec_sql} AS manufacturer_date_precision,
            CAST(init_fda_dt AS VARCHAR) AS initial_regulatory_date,
            {std_init_fda_dt_sql} AS standard_initial_regulatory_date,
            {init_fda_dt_prec_sql} AS initial_regulatory_date_precision,
            CAST(fda_dt AS VARCHAR) AS latest_regulatory_date,
            {std_fda_dt_sql} AS standard_latest_regulatory_date,
            {fda_dt_prec_sql} AS latest_regulatory_date_precision,
            CAST(rept_dt AS VARCHAR) AS report_date,
            {std_rept_dt_sql} AS standard_report_date,
            {rept_dt_prec_sql} AS report_date_precision,
            CAST(NULL AS VARCHAR) AS death_date,
            CAST(NULL AS DATE) AS standard_death_date,
            CAST(NULL AS VARCHAR) AS death_date_precision,
            CAST(NULL AS VARCHAR) AS confidentiality_flag,
            CAST(rept_cod AS VARCHAR) AS report_type_code,
            CAST(rept_cod AS VARCHAR) AS report_code,
            {rept_label_sql} AS report_type_label,
            CASE WHEN UPPER(TRIM(rept_cod)) = 'EXP' THEN 'Y' ELSE 'N' END AS expedited_flag,
            CAST(e_sub AS VARCHAR) AS electronic_submission_flag,
            CAST(mfr_num AS VARCHAR) AS manufacturer_control_number,
            CAST(mfr_num AS VARCHAR) AS manufacturer_num,
            CAST(mfr_sndr AS VARCHAR) AS manufacturer_name,
            CAST(mfr_sndr AS VARCHAR) AS manufacturer_sender,
            CAST(auth_num AS VARCHAR) AS auth_num,
            CAST(lit_ref AS VARCHAR) AS lit_ref,
            CAST(to_mfr AS VARCHAR) AS to_mfr,
            CAST(NULL AS VARCHAR) AS sender_type_code,
            CAST(NULL AS VARCHAR) AS sender_type_label,
            TRY_CAST(age AS DOUBLE) AS reported_age,
            CAST(age_cod AS VARCHAR) AS reported_age_code,
            CAST(age_grp AS VARCHAR) AS age_group_code,
            CAST(age_grp AS VARCHAR) AS reported_age_group_code,
            CAST(sex AS VARCHAR) AS reported_sex_code,
            TRY_CAST(wt AS DOUBLE) AS reported_weight,
            CAST(wt_cod AS VARCHAR) AS reported_weight_code,
            CAST(occp_cod AS VARCHAR) AS reporter_occupation_code,
            {occp_label_sql} AS reporter_occupation_label,
            CAST(reporter_country AS VARCHAR) AS reporter_country,
            CAST(occr_country AS VARCHAR) AS occurrence_country,
            {age_sql} AS standard_age_years,
            {sex_label_sql} AS standard_sex_label,
            {wt_sql} AS standard_weight_kg,
            'FDA_FAERS_ASCII' AS _source_system,
            '{data_period}' AS _data_period,
            '{file_path.name}' AS _source_file,
            'S3' AS _source_signature_id,
            CURRENT_TIMESTAMP AS _ingested_at
        FROM read_csv('{file_path.as_posix()}', delim='$', header=True, all_varchar=True, quote='', escape='', ignore_errors=true, null_padding=true);
    """)


def load_s3_drug(con: duckdb.DuckDBPyConnection, file_path: Path, data_period: str):
    """Loads S3 DRUG file into canonical drug table."""
    role_label_sql = get_drug_role_label_sql("role_cod")
    dechal_lbl_sql = get_dechallenge_label_sql("dechal")
    rechal_lbl_sql = get_rechallenge_label_sql("rechal")
    std_exp_dt_sql = get_standard_date_sql("exp_dt")
    exp_dt_prec_sql = get_date_precision_sql("exp_dt")
    con.execute(f"""
        CREATE OR REPLACE TABLE drug AS
        SELECT
            CAST(primaryid AS VARCHAR) AS primary_id,
            CAST(caseid AS VARCHAR) AS case_id,
            COALESCE(NULLIF(TRIM(CAST(drug_seq AS VARCHAR)), ''), '1') AS drug_seq,
            CAST(drugname AS VARCHAR) AS reported_drug_name,
            CAST(prod_ai AS VARCHAR) AS reported_active_ingredient,
            CAST(val_vbm AS VARCHAR) AS reported_validation_code,
            CAST(role_cod AS VARCHAR) AS role_code,
            {role_label_sql} AS role_label,
            CAST(route AS VARCHAR) AS route,
            CAST(dose_vbm AS VARCHAR) AS reported_dose_verbatim,
            TRY_CAST(dose_amt AS DOUBLE) AS dose_amount,
            CAST(dose_unit AS VARCHAR) AS dose_unit,
            CAST(dose_form AS VARCHAR) AS dose_form,
            CAST(dose_freq AS VARCHAR) AS dose_frequency,
            CAST(cum_dose_chr AS VARCHAR) AS cumulative_dose_amount,
            CAST(cum_dose_unit AS VARCHAR) AS cumulative_dose_unit,
            CAST(dechal AS VARCHAR) AS dechallenge_code,
            {dechal_lbl_sql} AS dechallenge_label,
            CAST(rechal AS VARCHAR) AS rechallenge_code,
            {rechal_lbl_sql} AS rechallenge_label,
            CAST(lot_num AS VARCHAR) AS lot_number,
            CAST(exp_dt AS VARCHAR) AS expiration_date,
            {std_exp_dt_sql} AS standard_expiration_date,
            {exp_dt_prec_sql} AS expiration_date_precision,
            CAST(nda_num AS VARCHAR) AS regulatory_auth_num,
            TRIM(UPPER(CAST(drugname AS VARCHAR))) AS structural_clean_drug_name,
            CAST(NULL AS VARCHAR) AS standard_concept_name,
            CAST(NULL AS VARCHAR) AS standard_concept_source,
            CAST(NULL AS VARCHAR) AS rxcui,
            'NOT_ATTEMPTED' AS derivation_status,
            'FDA_FAERS_ASCII' AS _source_system,
            '{data_period}' AS _data_period,
            '{file_path.name}' AS _source_file,
            'S3' AS _source_signature_id,
            CURRENT_TIMESTAMP AS _ingested_at
        FROM read_csv('{file_path.as_posix()}', delim='$', header=True, all_varchar=True, quote='', escape='', ignore_errors=true, null_padding=true);
    """)


def load_s3_reac(con: duckdb.DuckDBPyConnection, file_path: Path, data_period: str):
    """Loads S3 REAC file into canonical reac table."""
    con.execute(f"""
        CREATE OR REPLACE TABLE reac AS
        SELECT
            CAST(primaryid AS VARCHAR) AS primary_id,
            CAST(caseid AS VARCHAR) AS case_id,
            CAST(pt AS VARCHAR) AS reported_reaction_term,
            ROW_NUMBER() OVER (PARTITION BY primaryid) AS reaction_seq,
            CAST(drug_rec_act AS VARCHAR) AS drug_reaction_action,
            'FDA_FAERS_ASCII' AS _source_system,
            '{data_period}' AS _data_period,
            '{file_path.name}' AS _source_file,
            'S3' AS _source_signature_id,
            CURRENT_TIMESTAMP AS _ingested_at
        FROM read_csv('{file_path.as_posix()}', delim='$', header=True, all_varchar=True, quote='', escape='', ignore_errors=true, null_padding=true);
    """)


def load_s3_outc(con: duckdb.DuckDBPyConnection, file_path: Path, data_period: str):
    """Loads S3 OUTC file into canonical outc table."""
    outc_lbl_sql = get_outcome_label_sql("outc_cod")
    serious_sql = get_outcome_is_serious_sql("outc_cod")
    con.execute(f"""
        CREATE OR REPLACE TABLE outc AS
        SELECT
            CAST(primaryid AS VARCHAR) AS primary_id,
            CAST(caseid AS VARCHAR) AS case_id,
            CAST(outc_cod AS VARCHAR) AS outcome_code,
            {outc_lbl_sql} AS outcome_label,
            {serious_sql} AS is_serious,
            'FDA_FAERS_ASCII' AS _source_system,
            '{data_period}' AS _data_period,
            '{file_path.name}' AS _source_file,
            'S3' AS _source_signature_id,
            CURRENT_TIMESTAMP AS _ingested_at
        FROM read_csv('{file_path.as_posix()}', delim='$', header=True, all_varchar=True, quote='', escape='', ignore_errors=true, null_padding=true);
    """)


def load_s3_indi(con: duckdb.DuckDBPyConnection, file_path: Path, data_period: str):
    """Loads S3 INDI file into canonical indi table."""
    load_standard_indi(con, file_path, data_period, signature_id="S3")


def load_s3_ther(con: duckdb.DuckDBPyConnection, file_path: Path, data_period: str):
    """Loads S3 THER file into canonical ther table."""
    load_standard_ther(con, file_path, data_period, signature_id="S3")


def load_s3_rpsr(con: duckdb.DuckDBPyConnection, file_path: Path, data_period: str):
    """Loads S3 RPSR file into canonical rpsr table."""
    load_standard_rpsr(con, file_path, data_period, signature_id="S3")
