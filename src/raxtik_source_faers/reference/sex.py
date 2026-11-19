"""Official FDA / ICH Patient Sex Codes (GNDR_COD / SEX)."""

from __future__ import annotations

from typing import List

from raxtik_etl.reference.codes import ReferenceCodeEntry

FDA_SEX_REFERENCE: List[ReferenceCodeEntry] = [
    ReferenceCodeEntry(
        "M", "Male", "Male patient", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True
    ),
    ReferenceCodeEntry(
        "F",
        "Female",
        "Female patient",
        "FDA_CDER",
        "FAERS_QDE_ASC_NTS",
        "1.0.0",
        "2004Q1",
        None,
        True,
    ),
    ReferenceCodeEntry(
        "UNK",
        "Unknown",
        "Patient sex unknown at time of report",
        "FDA_CDER",
        "FAERS_QDE_ASC_NTS",
        "1.0.0",
        "2004Q1",
        None,
        True,
    ),
    ReferenceCodeEntry(
        "NS",
        "Not Specified",
        "Patient sex not specified by reporter (legacy)",
        "FDA_CDER",
        "AERS_DOCUMENTATION",
        "1.0.0",
        "2004Q1",
        "2012Q3",
        False,
    ),
]
