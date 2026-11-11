"""Official FDA Patient Age Group Codes (AGE_GRP)."""

from __future__ import annotations

from typing import List

from raxtik_etl.reference.codes import ReferenceCodeEntry

FDA_AGE_GROUPS_REFERENCE: List[ReferenceCodeEntry] = [
    ReferenceCodeEntry(
        "N",
        "Neonate",
        "Neonate (birth to 27 days)",
        "FDA_CDER",
        "FAERS_QDE_ASC_NTS",
        "1.0.0",
        "2014Q3",
        None,
        True,
    ),
    ReferenceCodeEntry(
        "I",
        "Infant",
        "Infant (28 days to 23 months)",
        "FDA_CDER",
        "FAERS_QDE_ASC_NTS",
        "1.0.0",
        "2014Q3",
        None,
        True,
    ),
    ReferenceCodeEntry(
        "C",
        "Child",
        "Child (2 years to 11 years)",
        "FDA_CDER",
        "FAERS_QDE_ASC_NTS",
        "1.0.0",
        "2014Q3",
        None,
        True,
    ),
    ReferenceCodeEntry(
        "T",
        "Adolescent",
        "Adolescent (12 years to 17 years)",
        "FDA_CDER",
        "FAERS_QDE_ASC_NTS",
        "1.0.0",
        "2014Q3",
        None,
        True,
    ),
    ReferenceCodeEntry(
        "A",
        "Adult",
        "Adult (18 years to 64 years)",
        "FDA_CDER",
        "FAERS_QDE_ASC_NTS",
        "1.0.0",
        "2014Q3",
        None,
        True,
    ),
    ReferenceCodeEntry(
        "E",
        "Elderly",
        "Elderly (65 years and older)",
        "FDA_CDER",
        "FAERS_QDE_ASC_NTS",
        "1.0.0",
        "2014Q3",
        None,
        True,
    ),
]
