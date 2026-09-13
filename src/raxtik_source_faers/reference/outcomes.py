"""Official FDA Patient Outcome Reference Codes (OUTC_COD)."""

from __future__ import annotations

from typing import List

from raxtik_etl.reference.codes import ReferenceCodeEntry

FDA_OUTCOMES_REFERENCE: List[ReferenceCodeEntry] = [
    ReferenceCodeEntry(
        "DE",
        "Death",
        "Results in death",
        "FDA_CDER",
        "FAERS_QDE_README",
        "1.0.0",
        "2004Q1",
        None,
        True,
    ),
    ReferenceCodeEntry(
        "LT",
        "Life-Threatening",
        "Life-threatening adverse event",
        "FDA_CDER",
        "FAERS_QDE_README",
        "1.0.0",
        "2004Q1",
        None,
        True,
    ),
    ReferenceCodeEntry(
        "HO",
        "Hospitalization",
        "Initial or prolonged hospitalization",
        "FDA_CDER",
        "FAERS_QDE_README",
        "1.0.0",
        "2004Q1",
        None,
        True,
    ),
    ReferenceCodeEntry(
        "DS",
        "Disability",
        "Disability or permanent damage",
        "FDA_CDER",
        "FAERS_QDE_README",
        "1.0.0",
        "2004Q1",
        None,
        True,
    ),
    ReferenceCodeEntry(
        "CA",
        "Congenital Anomaly",
        "Congenital anomaly or birth defect",
        "FDA_CDER",
        "FAERS_QDE_README",
        "1.0.0",
        "2004Q1",
        None,
        True,
    ),
    ReferenceCodeEntry(
        "RI",
        "Required Intervention",
        "Required intervention to prevent permanent impairment",
        "FDA_CDER",
        "FAERS_QDE_README",
        "1.0.0",
        "2004Q1",
        None,
        True,
    ),
    ReferenceCodeEntry(
        "OT",
        "Other Serious",
        "Other serious or medically important event",
        "FDA_CDER",
        "FAERS_QDE_README",
        "1.0.0",
        "2004Q1",
        None,
        True,
    ),
]
