"""Official FDA Patient Age Measurement Unit Codes (AGE_COD)."""

from __future__ import annotations

from typing import List

from raxtik_etl.reference.codes import ReferenceCodeEntry

FDA_AGE_UNITS_REFERENCE: List[ReferenceCodeEntry] = [
    ReferenceCodeEntry("YR", "Years", "Age measured in calendar years", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("DEC", "Decades", "Age measured in decades (10 years)", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("MON", "Months", "Age measured in months", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("WK", "Weeks", "Age measured in weeks", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("DY", "Days", "Age measured in days", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
    ReferenceCodeEntry("HR", "Hours", "Age measured in hours", "FDA_CDER", "FAERS_QDE_ASC_NTS", "1.0.0", "2004Q1", None, True),
]
