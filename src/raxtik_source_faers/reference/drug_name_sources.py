"""Official FDA Drug Name Validation Codes (VAL_VBM)."""

from __future__ import annotations

from typing import List

from raxtik_etl.reference.codes import ReferenceCodeEntry

FDA_DRUG_NAME_SOURCES_REFERENCE: List[ReferenceCodeEntry] = [
    ReferenceCodeEntry(
        "1",
        "Validated Trade Name",
        "Product name matches an FDA-validated trade name in dictionary",
        "FDA_CDER",
        "FAERS_QDE_ASC_NTS",
        "1.0.0",
        "2004Q1",
        None,
        True,
    ),
    ReferenceCodeEntry(
        "2",
        "Verbatim Name",
        "Product name is the verbatim text exactly as reported by submitter",
        "FDA_CDER",
        "FAERS_QDE_ASC_NTS",
        "1.0.0",
        "2004Q1",
        None,
        True,
    ),
]
