# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.0.dev1 - 2026-11-19

**Full Changelog**: https://github.com/raxtik-org/raxtik-source-faers/commits/v0.1.0.dev1

### Added
- Official FDA FAERS/AERS data source connector, signature resolver, and canonical extractor for `raxtik-etl`.
- Fail-closed historical schema identification across S1 (2004Q1–2012Q3), S2 (2012Q4–2014Q2), and S3 (2014Q3–present) eras.
- Raw ASCII extract staging handling `$`-delimited records, embedded newlines, and legacy column header aliases.
- Embedded clinical reference codelists for administration routes, dosage formulations, and reporter occupations.
- Specialized `FAERS` client registered via Python entry points inheriting from `BaseDataset`.
- Standalone documentation site on ReadTheDocs with interactive Mermaid diagrams.
