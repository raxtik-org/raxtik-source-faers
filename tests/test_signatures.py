"""Unit tests for FAERS Fail-Closed Signature Resolver."""

from __future__ import annotations

import io
import zipfile

import pytest

from raxtik_source_faers.signatures.resolver import detect_archive_signature


@pytest.mark.parametrize(
    ("filename", "content", "data_period", "expected_sig", "expected_err"),
    [
        (
            "DEMO04Q1.txt",
            "ISR$CASE$I_F_COD$FOLL_SEQ$IMAGE$EVENT_DT$MFR_DT$FDA_DT$REPT_COD$MFR_NUM$MFR_SNDR$AGE$AGE_COD$GNDR_COD$E_SUB$WT$WT_COD$REPT_DT$OCCP_COD$DEATH_DT$TO_MFR$CONFID\n",
            "2004Q1",
            "S1",
            None,
        ),
        (
            "DEMO12Q4.txt",
            "primaryid$caseid$caseversion$i_f_code$event_dt$mfr_dt$init_fda_dt$fda_dt$rept_cod$mfr_num$mfr_sndr$age$age_cod$gndr_cod$e_sub$wt$wt_cod$rept_dt$to_mfr$occp_cod$reporter_country$occr_country\n",
            "2012Q4",
            "S2",
            None,
        ),
        (
            "DEMO14Q3.txt",
            "primaryid$caseid$caseversion$i_f_code$event_dt$mfr_dt$init_fda_dt$fda_dt$rept_cod$auth_num$mfr_num$mfr_sndr$lit_ref$age$age_cod$age_grp$sex$e_sub$wt$wt_cod$rept_dt$to_mfr$occp_cod$reporter_country$occr_country\n",
            "2014Q3",
            "S3",
            None,
        ),
        (
            "DEMO99Q9.txt",
            "UNKNOWN_COL1$UNKNOWN_COL2$FOOBAR\n1$2$3\n",
            "1999Q9",
            None,
            r"Unrecognized FDA ASCII schema signature",
        ),
        (
            "DRUG04Q1.txt",
            "ISR$DRUG_SEQ$DRUGNAME\n",
            "2004Q1",
            None,
            r"No DEMO table found",
        ),
    ],
)
def test_signature_resolution(
    filename: str,
    content: str,
    data_period: str,
    expected_sig: str | None,
    expected_err: str | None,
) -> None:
    """Verify archive signature resolution and fail-closed validation across schemas."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(filename, content)
    buf.seek(0)
    with zipfile.ZipFile(buf, "r") as zf:
        if expected_err:
            with pytest.raises(ValueError, match=expected_err):
                detect_archive_signature(zf, data_period=data_period)
        else:
            assert detect_archive_signature(zf, data_period=data_period) == expected_sig
