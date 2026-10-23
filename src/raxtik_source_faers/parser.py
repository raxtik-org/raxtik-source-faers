"""Streaming 569Xdelimited parser for FDA FAERS/AERS ASCII raw data files."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any, Dict, Generator, Optional, Union


def detect_table_type(filename_or_path: Union[str, Path]) -> Optional[str]:
    """Detect canonical table type from a FAERS/AERS filename.

    Supports:
    - DEMO / demo -> demo
    - DRUG / drug -> drug
    - REAC / reac -> reac
    - OUTC / outc -> outc
    - INDI / indi -> indi
    - THER / ther -> ther
    - RPSR / rpsr -> rpsr
    """
    name = Path(filename_or_path).name.upper()
    if name.startswith("DEMO"):
        return "demo"
    elif name.startswith("DRUG"):
        return "drug"
    elif name.startswith("REAC"):
        return "reac"
    elif name.startswith("OUTC"):
        return "outc"
    elif name.startswith("INDI"):
        return "indi"
    elif name.startswith("THER"):
        return "ther"
    elif name.startswith("RPSR"):
        return "rpsr"
    return None


def clean_field_name(name: str) -> str:
    """Normalize header field names to snake_case lowercase."""
    name = name.strip().lower()
    name = re.sub(r"[^\w]+", "_", name)
    name = re.sub(r"^_+|_+$", "", name)
    return name


def parse_faers_ascii_file(
    file_path: Union[Path, str],
    table_type: Optional[str] = None,
    chunk_size: int = 10000,
) -> Generator[Dict[str, Any], None, None]:
    """Stream and parse a 569Xdelimited FAERS ASCII file into dictionary records.

    Handles encoding fallbacks (utf-8, iso-8859-1, latin-1, cp1252) and standardizes
    field names.

    Args:
        file_path: Path to the .txt ASCII file.
        table_type: Optional canonical table name hint.
        chunk_size: Processing batch size.

    Yields:
        Standardized record dictionary.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"FAERS ASCII file not found: {path}")

    resolved_table_type = table_type or detect_table_type(path)

    encodings = ["utf-8", "iso-8859-1", "latin-1", "cp1252"]
    file_obj = None

    for enc in encodings:
        try:
            file_obj = open(path, "r", encoding=enc, errors="replace")
            file_obj.readline()
            file_obj.seek(0)
            break
        except Exception:
            if file_obj:
                file_obj.close()
                file_obj = None

    if file_obj is None:
        raise OSError(f"Unable to open {path} with any supported encoding.")

    try:
        reader = csv.reader(file_obj, delimiter="$", quoting=csv.QUOTE_NONE)
        raw_headers = next(reader, None)
        if not raw_headers:
            return

        headers = [clean_field_name(h) for h in raw_headers]

        for row in reader:
            if not row or not any(row):
                continue

            record: Dict[str, Any] = {}
            for i, val in enumerate(row):
                if i < len(headers):
                    v = val.strip() if val else None
                    record[headers[i]] = v if v != "" else None

            if resolved_table_type:
                record["_table_type"] = resolved_table_type

            yield record

    finally:
        file_obj.close()
