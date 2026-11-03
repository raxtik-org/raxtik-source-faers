"""Fail-Closed Signature Resolver for FDA Quarterly ASCII Archives."""

from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional

DEFAULT_DELIMITER = "$"


class ArchiveSignature(StrEnum):
    """Verified FDA Quarterly ASCII Schema Signatures."""

    S1 = "S1"  # Legacy AERS (2004Q1 - 2012Q3)
    S2 = "S2"  # FAERS Migration (2012Q4 - 2014Q2)
    S3 = "S3"  # Modern FAERS & AEMS (2014Q3 - Present)


@dataclass(frozen=True)
class SignatureRule:
    """Declarative signature matching rule based on column sets."""

    signature: ArchiveSignature
    required_columns: frozenset[str]
    any_of_columns: frozenset[str] = frozenset()

    def matches(self, columns: set[str]) -> bool:
        """Check if archive columns satisfy rule requirements."""
        if not self.required_columns.issubset(columns):
            return False
        if self.any_of_columns and not bool(self.any_of_columns & columns):
            return False
        return True


# Declarative signature rules evaluated in priority order
SIGNATURE_RULES: tuple[SignatureRule, ...] = (
    # S1: Characterized by ISR as primary key and CASE as case key (2004Q1 - 2012Q3)
    SignatureRule(
        signature=ArchiveSignature.S1,
        required_columns=frozenset({"isr", "case"}),
    ),
    # S2: Characterized by PRIMARYID, CASEID, CASEVERSION, and GNDR_COD (2012Q4 - 2014Q2)
    SignatureRule(
        signature=ArchiveSignature.S2,
        required_columns=frozenset({"primaryid", "caseid", "gndr_cod"}),
    ),
    # S3: Modern FAERS & AEMS (2014Q3 - Present, including 2025/2026+)
    SignatureRule(
        signature=ArchiveSignature.S3,
        required_columns=frozenset({"primaryid", "caseid"}),
        any_of_columns=frozenset({"sex", "age_grp", "auth_num"}),
    ),
)


def detect_archive_signature(
    zf: zipfile.ZipFile,
    data_period: Optional[str] = None,
    delimiter: str = DEFAULT_DELIMITER,
) -> ArchiveSignature:
    """Detects whether an archive matches Signature S1, S2, or S3 using strict header inspection.

    Args:
        zf: Open ZipFile instance containing FAERS extract files.
        data_period: Temporal quarter identifier (e.g. '2004Q1', '2025Q1').
        delimiter: Column delimiter used in extract files (default '$').

    Returns:
        Detected signature identifier (ArchiveSignature enum: S1, S2, or S3).

    Raises:
        ValueError: If archive headers do not match any verified historical signature,
            or if the DEMO table is missing.
    """
    file_list = zf.namelist()
    demo_files = [
        f for f in file_list if re.search(r"(?:^|[/\\])DEMO[^/\\]*\.txt$", f, re.IGNORECASE)
    ]
    if not demo_files:
        raise ValueError(
            f"Invalid FAERS archive: No DEMO table found in {data_period or 'archive'}"
        )

    with zf.open(demo_files[0]) as f:
        header_line = f.readline().decode("utf-8", errors="ignore").strip()

    columns = {c.strip().lower() for c in header_line.split(delimiter) if c.strip()}

    for rule in SIGNATURE_RULES:
        if rule.matches(columns):
            return rule.signature

    raise ValueError(
        f"Unrecognized FDA ASCII schema signature for data period {data_period or 'unknown'}. "
        f"Detected DEMO columns: {sorted(list(columns))[:10]}... "
        f"Ensure archive matches S1 (ISR), S2 (PRIMARYID+GNDR_COD), or S3 (PRIMARYID+SEX)."
    )
