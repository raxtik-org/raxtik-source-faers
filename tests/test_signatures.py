"""Unit tests for FAERS Fail-Closed Signature Resolver."""

import io
import zipfile

import pytest
from raxtik_source_faers.signatures.resolver import detect_archive_signature


def test_s1_signature_detection():
    """Verify S1 signature detection (ISR + CASE in DEMO)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(
            "DEMO04Q1.txt",
            "ISR$CASE$I_F_COD$FOLL_SEQ$IMAGE$EVENT_DT$MFR_DT$FDA_DT$REPT_COD$MFR_NUM$MFR_SNDR$AGE$AGE_COD$GNDR_COD$E_SUB$WT$WT_COD$REPT_DT$OCCP_COD$DEATH_DT$TO_MFR$CONFID\n",
        )
    buf.seek(0)
    with zipfile.ZipFile(buf, "r") as zf:
        sig = detect_archive_signature(zf, release="2004Q1")
        assert sig == "S1"


def test_s2_signature_detection():
    """Verify S2 signature detection (PRIMARYID + CASEID + GNDR_COD in DEMO)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(
            "DEMO12Q4.txt",
            "primaryid$caseid$caseversion$i_f_code$event_dt$mfr_dt$init_fda_dt$fda_dt$rept_cod$mfr_num$mfr_sndr$age$age_cod$gndr_cod$e_sub$wt$wt_cod$rept_dt$to_mfr$occp_cod$reporter_country$occr_country\n",
        )
    buf.seek(0)
    with zipfile.ZipFile(buf, "r") as zf:
        sig = detect_archive_signature(zf, release="2012Q4")
        assert sig == "S2"


def test_s3_signature_detection():
    """Verify S3 signature detection (PRIMARYID + CASEID + SEX in DEMO)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(
            "DEMO14Q3.txt",
            "primaryid$caseid$caseversion$i_f_code$event_dt$mfr_dt$init_fda_dt$fda_dt$rept_cod$auth_num$mfr_num$mfr_sndr$lit_ref$age$age_cod$age_grp$sex$e_sub$wt$wt_cod$rept_dt$to_mfr$occp_cod$reporter_country$occr_country\n",
        )
    buf.seek(0)
    with zipfile.ZipFile(buf, "r") as zf:
        sig = detect_archive_signature(zf, release="2014Q3")
        assert sig == "S3"


def test_fail_closed_on_unknown_schema():
    """Verify that unknown/malformed archives fail closed with explicit ValueError."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("DEMO99Q9.txt", "UNKNOWN_COL1$UNKNOWN_COL2$FOOBAR\n1$2$3\n")
    buf.seek(0)
    with zipfile.ZipFile(buf, "r") as zf:
        with pytest.raises(ValueError, match="Unrecognized FDA ASCII schema signature"):
            detect_archive_signature(zf, release="1999Q9")


def test_fail_closed_on_missing_demo():
    """Verify error when DEMO table is completely missing from archive."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("DRUG04Q1.txt", "ISR$DRUG_SEQ$DRUGNAME\n")
    buf.seek(0)
    with zipfile.ZipFile(buf, "r") as zf:
        with pytest.raises(ValueError, match="No DEMO table found"):
            detect_archive_signature(zf, release="2004Q1")
