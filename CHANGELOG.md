# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-11-26

**Full Changelog**: https://github.com/raxtik-org/raxtik-source-faers/compare/v0.1.0.dev2...v0.1.0

### Added
- First stable release of `raxtik-source-faers`, aligned with `raxtik-etl>=0.1.0,<0.2.0` and the verified 91-quarter (`2004Q1..2026Q3`) FAERS/AERS dataset (`v0.1.0`) on Hugging Face Hub.
- Fail-closed mandatory table enforcement (`demo`, `drug`, `reac`) in `FAERSAdapter.extract_and_load()`.
- PyPI SEO & funding metadata and Silver Tier README quickstart.

### Fixed
- Propagate unexpected (non-`CatalogException`) DuckDB errors during table row counting instead of defaulting to `0`.

## [0.1.0.dev2] - 2026-11-25

**Full Changelog**: https://github.com/raxtik-org/raxtik-source-faers/compare/v0.1.0.dev1...v0.1.0.dev2

### Added
- Silver Tier index support in `FAERS` client (`tier="silver"`, `index_dir`, `cache_index`, `as_of_period`).
- `get_resolution_policy()` hook on `FAERSAdapter` (`policy_version="faers-1.0.0"`) for cross-quarter case resolution.

### Fixed
- Deterministic numeric ordering (`TRY_CAST(drug_seq AS INTEGER) NULLS LAST, drug_seq`) in `case_adverse_events_summary` analytical view.

### Changed
- Updated minimum dependency to `raxtik-etl>=0.1.0.dev3`.

## [0.1.0.dev1] - 2026-11-19

**Full Changelog**: https://github.com/raxtik-org/raxtik-source-faers/commits/v0.1.0.dev1

### Added
- Official FDA FAERS/AERS data source connector, signature resolver, and canonical extractor for `raxtik-etl`.
- Fail-closed historical schema identification across S1 (2004Q1–2012Q3), S2 (2012Q4–2014Q2), and S3 (2014Q3–present) eras.
- Raw ASCII extract staging handling `$`-delimited records, embedded newlines, and legacy column header aliases.
- Embedded clinical reference codelists for administration routes, dosage formulations, and reporter occupations.
- Specialized `FAERS` client registered via Python entry points inheriting from `BaseDataset`.
- Standalone documentation site on ReadTheDocs with interactive Mermaid diagrams.
