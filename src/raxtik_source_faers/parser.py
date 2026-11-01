"""Streaming dollar-delimited parser for FDA FAERS/AERS ASCII raw data files."""

from __future__ import annotations

from collections.abc import Generator, Mapping
from pathlib import Path
from typing import Any

from raxtik_etl.sources import (
    clean_field_name,
    detect_file_entity,
    parse_delimited_file,
)

from raxtik_source_faers.constants import TABLE_PREFIX_TO_ENTITY


def detect_table_type(
    filename_or_path: str | Path,
    prefix_mapping: Mapping[str, str] | None = None,
) -> str | None:
    """Detect canonical table type from a FAERS/AERS filename or custom mapping.

    Supports:
    - DEMO / demo -> demo
    - DRUG / drug -> drug
    - REAC / reac -> reac
    - OUTC / outc -> outc
    - INDI / indi -> indi
    - THER / ther -> ther
    - RPSR / rpsr -> rpsr
    """
    mapping = prefix_mapping if prefix_mapping is not None else TABLE_PREFIX_TO_ENTITY
    return detect_file_entity(filename_or_path, prefix_mapping=mapping)


def parse_faers_ascii_file(
    file_path: Path | str,
    table_type: str | None = None,
    chunk_size: int = 10000,
) -> Generator[dict[str, Any], None, None]:
    """Stream and parse a dollar-delimited FAERS ASCII file into dictionary records.

    Handles encoding fallbacks (utf-8, iso-8859-1, latin-1, cp1252) and standardizes
    field names.

    Args:
        file_path: Path to the .txt ASCII file.
        table_type: Optional canonical table name hint.
        chunk_size: Processing batch size.

    Yields:
        Standardized record dictionary.
    """
    yield from parse_delimited_file(
        file_path=file_path,
        delimiter="$",
        table_type=table_type,
        prefix_mapping=TABLE_PREFIX_TO_ENTITY,
    )


__all__ = [
    "clean_field_name",
    "detect_file_entity",
    "detect_table_type",
    "parse_delimited_file",
    "parse_faers_ascii_file",
]
