# raxtik-source-faers Documentation

Official FDA FAERS/AERS data source connector, signature resolver, and canonical extractor for `raxtik-etl`.

---

```{toctree}
:maxdepth: 2
:caption: Getting Started

self
architecture
reference_codelists
api
```

```{toctree}
:maxdepth: 2
:caption: Community & Contributing

contributing
contributors
```

---

## 🏛️ Overview

`raxtik-source-faers` is an independent plugin that implements the `SourceAdapter` protocol for `raxtik-etl`. It isolates all FDA-specific archive formats, legacy ASCII quirks, and historical schema evolution from the canonical data platform:

- **Fail-closed signature resolution**: Accurately classifies releases into **S1**, **S2**, or **S3** schemas.
- **Raw ASCII extract staging**: Safely parses `$`-delimited text files, embedded line-breaks, and historical field aliases.
- **Reference codelists**: Embedded clinical lookup tables for FDA CDER routes, dosage forms, and reporter roles.
- **Zero-core coupling**: Registers via Python standard entry points without requiring any FAERS-specific logic inside `raxtik-etl`.

---

## 🔍 Historical FDA Signatures (Fail-Closed)

The FDA has altered table schemas, column names, delimiters, and file headers across historical eras:

| Era | Signature | Delimiter | Case ID Column | Key Schema Differences |
| :--- | :---: | :---: | :---: | :--- |
| **Legacy AERS** (2004Q1 – 2012Q3) | **`S1`** | `$` / comma | `isr` | Uses `isr` as report primary key, `case` as case identifier. |
| **Early FAERS** (2012Q4 – 2014Q2) | **`S2`** | `$` | `primaryid` | Migrated to `primaryid` and `caseid`. Standard ASCII headers. |
| **Modern FAERS** (2014Q3 – Present) | **`S3`** | `$` | `primaryid` | Modern MedDRA and ICH E2B(R2)/(R3) aligned field layout. |

Signature detection is **fail-closed**: any unrecognized or malformed archive raises an immediate exception rather than ingesting corrupt data.

---

## 💻 Quickstart: Python Client

`raxtik-source-faers` provides the dedicated `FAERS` dataset client:

```python
from raxtik_etl import FAERS

# 1. Download and query locally
with FAERS.from_hf("2024Q1") as faers:
    faers.print_summary()
    cases_df = faers.cases(limit=100)
    drugs_df = faers.drugs(limit=100)
    reactions_df = faers.reactions(limit=100)

# 2. Zero-disk remote streaming over HTTPS
with FAERS.from_hf("2024Q1", remote=True) as faers:
    cases_df = faers.cases(limit=100)
    print(cases_df)
```

---

## 📦 Reference Codelists

Standard reference codelists are built into `raxtik_source_faers.reference`:
- `FDA_ROUTE_REFERENCE`: CDER administration route definitions.
- `FDA_FORM_REFERENCE`: Dosage form descriptions.
- `FDA_OCCP_REFERENCE`: Reporter occupation categories.
- `FDA_OUTC_REFERENCE`: Seriousness and outcome classifications.
- `ICH_ISO_COUNTRIES_REFERENCE`: ISO 3166-1 alpha-2 country mappings.