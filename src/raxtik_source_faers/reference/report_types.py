"""Official FDA Report Type Codes (REPT_COD)."""

from __future__ import annotations

from typing import List

from raxtik_etl.reference.codes import ReferenceCodeEntry

FDA_REPORT_TYPES_REFERENCE: List[ReferenceCodeEntry] = [
    ReferenceCodeEntry(
        "EXP",
        "Expedited (15-Day)",
        "15-day expedited report submitted by manufacturer for serious, unexpected adverse events",
        "FDA_CDER",
        "FAERS_QDE_ASC_NTS",
        "1.0.0",
        "2004Q1",
        None,
        True,
    ),
    ReferenceCodeEntry(
        "PER",
        "Periodic",
        "Periodic non-expedited safety report submitted by manufacturer under periodic reporting requirements",
        "FDA_CDER",
        "FAERS_QDE_ASC_NTS",
        "1.0.0",
        "2004Q1",
        None,
        True,
    ),
    ReferenceCodeEntry(
        "DIR",
        "Direct",
        "Direct voluntary report submitted to FDA by healthcare professionals, consumers, or user facilities",
        "FDA_CDER",
        "FAERS_QDE_ASC_NTS",
        "1.0.0",
        "2004Q1",
        None,
        True,
    ),
    ReferenceCodeEntry(
        "5DAY",
        "5-Day (Combination Product)",
        "5-day report submitted for drug-device combination products under 21 CFR Part 4",
        "FDA_CDER",
        "FAERS_QDE_ASC_NTS",
        "1.0.0",
        "2022Q3",
        None,
        True,
    ),
    ReferenceCodeEntry(
        "30DAY",
        "30-Day (Combination Product)",
        "30-day report submitted for drug-device combination products under 21 CFR Part 4",
        "FDA_CDER",
        "FAERS_QDE_ASC_NTS",
        "1.0.0",
        "2022Q3",
        None,
        True,
    ),
]
