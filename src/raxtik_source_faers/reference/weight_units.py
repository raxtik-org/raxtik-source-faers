"""Official FDA Patient Weight Unit Codes (WT_COD)."""

from __future__ import annotations

from typing import List

from raxtik_etl.reference.codes import ReferenceCodeEntry

FDA_WEIGHT_UNITS_REFERENCE: List[ReferenceCodeEntry] = [
    ReferenceCodeEntry(
        "KG",
        "Kilograms",
        "Weight measured in kilograms",
        "FDA_CDER",
        "FAERS_QDE_ASC_NTS",
        "1.0.0",
        "2004Q1",
        None,
        True,
    ),
    ReferenceCodeEntry(
        "LBS",
        "Pounds",
        "Weight measured in pounds (avoirdupois)",
        "FDA_CDER",
        "FAERS_QDE_ASC_NTS",
        "1.0.0",
        "2004Q1",
        None,
        True,
    ),
    ReferenceCodeEntry(
        "GMS",
        "Grams",
        "Weight measured in grams",
        "FDA_CDER",
        "FAERS_QDE_ASC_NTS",
        "1.0.0",
        "2004Q1",
        None,
        True,
    ),
]
