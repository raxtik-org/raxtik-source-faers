# raxtik-source-faers

[![CI](https://github.com/raxtik-org/raxtik-source-faers/actions/workflows/ci.yml/badge.svg)](https://github.com/raxtik-org/raxtik-source-faers/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/raxtik-org/raxtik-source-faers/branch/main/graph/badge.svg)](https://codecov.io/gh/raxtik-org/raxtik-source-faers)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL_3.0-blue.svg)](./LICENSE)

Official FDA FAERS/AERS data source connector, signature resolver, and canonical extractor for `raxtik-etl`.

---

## 🏛 Overview

`raxtik-source-faers` is an independent plugin that implements the `SourceAdapter` protocol for `raxtik-etl`. It isolates all FDA-specific archive formats, legacy ASCII quirks, and historical schema evolution from the canonical data platform:

- **Fail-closed signature resolution**: Accurately classifies releases into **S1**, **S2**, or **S3** schemas.
- **Raw ASCII extract staging**: Safely parses `$`-delimited text files, embedded line-breaks, and historical field aliases.
- **Reference codelists**: Embedded clinical lookup tables for FDA CDER routes, dosage forms, and reporter roles.
- **Zero-core coupling**: Registers via Python standard entry points without requiring any FAERS-specific logic inside `raxtik-etl`.

---

## 🔍 Historical Signatures Handled

| Signature | Date Range | Primary Keys | Distinguishing Features |
| :--- | :--- | :--- | :--- |
| **`S1`** | 2004Q1 – 2012Q3 | `ISR`, `CASE` | Legacy AERS: `FOLL_SEQ`, `GNDR_COD`. Missing modern columns (`PROD_AI`, `AUTH_NUM`). |
| **`S2`** | 2012Q4 – 2014Q2 | `PRIMARYID`, `CASEID` | Migration Era: Transitional columns (`gndr_cod`, `lot_nbr`, `outc_code`). |
| **`S3`** | 2014Q3 – Present | `PRIMARYID`, `CASEID` | Modern FAERS/AEMS: `SEX`, `PROD_AI`, `AUTH_NUM`, `LIT_REF`, `DRUG_REC_ACT`. |

Signature detection is **fail-closed**: any unrecognized or malformed archive raises an explicit `ValueError` rather than silently defaulting to modern schemas.

---

## 🏛️ Canonical Data Model & Schema Mapping

The raw FDA ASCII files (`DEMO`, `DRUG`, `REAC`, `OUTC`, `INDI`, `THER`, `RPSR`) are projected into the unified canonical star-schema:

```mermaid
erDiagram
    demo ||--o{ drug : "primary_id"
    demo ||--o{ reac : "primary_id"
    demo ||--o{ outc : "primary_id"
    demo ||--o{ rpsr : "primary_id"
    drug ||--o{ indi : "primary_id, drug_seq"
    drug ||--o{ ther : "primary_id, drug_seq"

    demo {
        BIGINT primary_id PK "Unique submission report ID"
        BIGINT case_id "Unique patient case identifier"
        INTEGER case_version "Report version number"
        VARCHAR event_country "Country where reaction occurred"
        VARCHAR reporter_country_code "ISO 3166-1 alpha-2"
        DATE fda_date "Receipt date at FDA"
        VARCHAR age_group_code "ICH life stage classification"
        DOUBLE standard_age_years "Normalized age in decimal years"
        VARCHAR standard_sex_label "Male / Female / Unknown"
        DOUBLE standard_weight_kg "Normalized patient weight in kg"
        VARCHAR reporter_occupation_label "Physician, Pharmacist, Consumer..."
        VARCHAR report_type_label "Expedited 15-day, Periodic, Direct..."
    }

    drug {
        BIGINT primary_id FK "References demo.primary_id"
        INTEGER drug_seq PK "Unique exposure index per case"
        VARCHAR role_code "Role: PS, SS, C, I"
        VARCHAR standard_role_label "Primary Suspect, Concomitant..."
        VARCHAR reported_drug_name "Reported medicinal trade/brand name"
        VARCHAR active_ingredient "Normalized generic active substance"
        VARCHAR route "Administration route (Oral, IV...)"
        VARCHAR dose_form "Dosage formulation (Tablet, Solution...)"
        DOUBLE cumulative_dose "Normalized cumulative amount"
        VARCHAR cumulative_dose_unit_label "Metric dose unit (mg, mL...)"
    }

    reac {
        BIGINT primary_id FK "References demo.primary_id"
        VARCHAR reported_reaction_term PK "MedDRA Preferred Term"
        BIGINT reaction_seq "Reaction sequence ordinal"
        VARCHAR drug_reaction_action "Action taken with drug"
    }

    outc {
        BIGINT primary_id FK "References demo.primary_id"
        VARCHAR outc_code PK "Seriousness criterion: DE, HO, LT, DS, CA, RI, OT"
        VARCHAR standard_outc_label "Death, Hospitalization, Life-threatening..."
        BOOLEAN is_death "Flag for fatal outcome (DE)"
        BOOLEAN is_serious "Flag for serious adverse event"
    }

    indi {
        BIGINT primary_id FK "References drug.primary_id"
        INTEGER indi_drug_seq FK "References drug.drug_seq"
        VARCHAR indi_pt PK "MedDRA Preferred Term for clinical indication"
        VARCHAR reported_indication "Reported condition / disease treated"
    }

    ther {
        BIGINT primary_id FK "References drug.primary_id"
        INTEGER dsg_drug_seq FK "References drug.drug_seq"
        DATE start_date "Therapy initiation date"
        DATE end_date "Therapy cessation date"
        DOUBLE duration_days "Standardized duration in days"
    }

    rpsr {
        BIGINT primary_id FK "References demo.primary_id"
        VARCHAR rpsr_code PK "Report source classification code"
        VARCHAR standard_rpsr_label "Health Professional, Study, Consumer..."
    }
```

---

## 📦 Installation

Install alongside `raxtik-etl`:

```bash
pip install raxtik-source-faers raxtik-etl
```

Once installed, `raxtik-etl` automatically discovers the FAERS connector and provides the specialized `FAERS` dataset client.

---

## 🚀 Usage

### 1. Direct Hugging Face Loading & Streaming
Query precompiled quarterly packages from 2004Q1 through 2026Q3:

```python
from raxtik_etl import FAERS

# 1. Default (Fastest): Downloads once, caches locally, queries in milliseconds
with FAERS.from_hf("2024Q1") as faers:
    cases = faers.cases(limit=100)
    print(cases)

# 2. Zero-Disk Streaming: Streams directly over HTTPS without local downloads
with FAERS.from_hf("2024Q1", remote=True) as faers:
    cases = faers.cases(limit=100)
    print(cases)
```

### 2. Remote Querying via DuckDB (Zero Local Storage)
Query precompiled datasets on Hugging Face Hub over HTTPS without downloading full files to disk.

#### Option A: Remote DuckDB `ATTACH` (Single File URL, Full Schema & Views)
```python
import duckdb

con = duckdb.connect()
# httpfs is DuckDB's native C++ extension (no pip install required)
con.execute("INSTALL httpfs; LOAD httpfs;")

# 1 single URL attaches all 7 tables and the precomputed cases view
db_url = "https://huggingface.co/datasets/raxtik-org/faers-safety-database/resolve/main/bronze/2024/faers_2024Q1.duckdb"
con.execute(f"ATTACH '{db_url}' AS faers (READ_ONLY);")

con.execute("""
    SELECT d.reported_drug_name, COUNT(*) AS report_count
    FROM faers.drug d
    JOIN faers.reac r ON d.primary_id = r.primary_id
    WHERE d.role_code = 'PS' AND r.reported_reaction_term = 'Myocardial infarction'
    GROUP BY d.reported_drug_name ORDER BY report_count DESC LIMIT 5;
""").show()
```
> *Note: Initial ATTACH takes ~10s to load catalog metadata over HTTP, after which subsequent queries execute directly.*

#### Option B: Remote Parquet Scanning (Column Range Requests)
```python
import duckdb

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")

con.execute("""
    SELECT d.reported_drug_name, COUNT(*) AS report_count
    FROM 'https://huggingface.co/datasets/raxtik-org/faers-safety-database/resolve/main/bronze/2024/faers_2024Q1.parquet/drug.parquet' d
    JOIN 'https://huggingface.co/datasets/raxtik-org/faers-safety-database/resolve/main/bronze/2024/faers_2024Q1.parquet/reac.parquet' r
      ON d.primary_id = r.primary_id
    WHERE d.role_code = 'PS' AND r.reported_reaction_term = 'Myocardial infarction'
    GROUP BY d.reported_drug_name ORDER BY report_count DESC LIMIT 5;
""").show()
```

### 3. Download Quarterly FDA Archives
```python
from raxtik_source_faers import download_quarterly_archive

# Downloads and verifies official quarterly FDA archive zip
zip_path = download_quarterly_archive(year=2024, quarter=1, dest_dir="data/raw")
print(f"Downloaded to {zip_path}")
```

### 4. Extract into Canonical DuckDB via Adapter
```python
import duckdb
from pathlib import Path
from raxtik_etl.sources.protocol import SourceArtifact
from raxtik_source_faers import FAERSAdapter

con = duckdb.connect("my_database.duckdb")
adapter = FAERSAdapter()

artifact = SourceArtifact(path=Path("data/raw/faers_ascii_2024q1.zip"), release="2024Q1")

result = adapter.extract_and_load(con, artifact)
print(f"Extracted {result.row_counts['demo']} reports under signature {result.signature_id}")
```

---

## 👥 Contributors

See **[CONTRIBUTORS.md](CONTRIBUTORS.md)** for all project contributors.

---

## 📄 License
Licensed under the [GNU Affero General Public License v3.0 (AGPL-3.0)](./LICENSE).
