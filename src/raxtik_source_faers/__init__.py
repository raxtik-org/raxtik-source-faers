"""Official FDA FAERS/AEMS data connector, parser, and extractor for raxtik-etl."""

from raxtik_source_faers.adapter import FAERSAdapter
from raxtik_source_faers.fetcher import download_quarterly_archive, find_local_faers_files
from raxtik_source_faers.parser import clean_field_name, detect_table_type, parse_faers_ascii_file
from raxtik_source_faers.signatures.resolver import detect_archive_signature

__version__ = "0.1.0.dev0"

__all__ = [
    "FAERSAdapter",
    "download_quarterly_archive",
    "find_local_faers_files",
    "clean_field_name",
    "detect_table_type",
    "parse_faers_ascii_file",
    "detect_archive_signature",
    "__version__",
]
