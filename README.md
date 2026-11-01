# raxtik-source-faers

[![CI](https://github.com/raxtik-org/raxtik-source-faers/actions/workflows/ci.yml/badge.svg)](https://github.com/raxtik-org/raxtik-source-faers/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/raxtik-org/raxtik-source-faers/branch/main/graph/badge.svg)](https://codecov.io/gh/raxtik-org/raxtik-source-faers)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL_3.0-blue.svg)](./LICENSE)
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](#contributors)

Official FDA FAERS/AEMS data source connector, signature resolver, and canonical extractor for `raxtik-etl`.

---

## 🏛 Overview

`raxtik-source-faers` is an independent plugin that implements the `raxtik_etl.sources.protocol.SourceAdapter` protocol. It isolates all FDA-specific archive formats, legacy ASCII quirks, and historical schema evolution from the canonical data platform.

### Architectural Separation
```text
┌────────────────────────────────────────────────────────┐
│                   raxtik-source-faers                  │
│  - Fail-closed signature resolution (S1, S2, S3)       │
│  - Raw ASCII extract staging ($ delimiter, escapes)    │
│  - Historical column mapping rules (S1, S2, S3)        │
│  - FDA official reference code-sets (_code_*)          │
│  - Archive downloader & streaming ASCII parser         │
│  - Registers entry point: raxtik_etl.sources -> faers  │
└───────────────────────────┬────────────────────────────┘
                            │ Implements SourceAdapter
                            ▼
┌────────────────────────────────────────────────────────┐
│                      raxtik-etl                        │
│  - Canonical Schemas, Normalization, Case Resolution   │
│  - Packaging (DuckDB / Parquet) & Safety SDK           │
└────────────────────────────────────────────────────────┘
```

---

## 🔍 Historical Signatures Handled

| Signature | Date Range | Primary Keys | Distinguishing Features |
| :--- | :--- | :--- | :--- |
| **`S1`** | 2004Q1 – 2012Q3 | `ISR`, `CASE` | Legacy AERS: `FOLL_SEQ`, `GNDR_COD`. Missing modern columns (`PROD_AI`, `AUTH_NUM`). |
| **`S2`** | 2012Q4 – 2014Q2 | `PRIMARYID`, `CASEID` | Migration Era: Transitional columns (`gndr_cod`, `lot_nbr`, `outc_code`). |
| **`S3`** | 2014Q3 – Present | `PRIMARYID`, `CASEID` | Modern FAERS/AEMS: `SEX`, `PROD_AI`, `AUTH_NUM`, `LIT_REF`, `DRUG_REC_ACT`. |

Signature detection is **fail-closed**: any unrecognized or malformed archive raises an explicit `ValueError` rather than silently defaulting to modern schemas.

---

## 📦 Installation & Registration

Install in your environment alongside `raxtik-etl`:

```bash
pip install raxtik-source-faers
```

Or install with `raxtik-etl[faers]`:
```bash
pip install "raxtik-etl[faers]"
```

Once installed, the connector is automatically discovered by `raxtik-etl` via Python entry-points:
```toml
[project.entry-points."raxtik_etl.sources"]
faers = "raxtik_source_faers.adapter:FAERSAdapter"
```

---

## 🚀 Usage

### 1. Download Quarterly FDA Archives
```python
from raxtik_source_faers import download_quarterly_archive

# Downloads and verifies official quarterly FDA archive zip
zip_path = download_quarterly_archive(year=2024, quarter=1, dest_dir="data/raw")
print(f"Downloaded to {zip_path}")
```

### 2. Extract into Canonical DuckDB via Adapter
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

### 3. Stream & Parse Raw $-Delimited ASCII Files
```python
from raxtik_source_faers import parse_faers_ascii_file

for record in parse_faers_ascii_file("DEMO24Q1.txt", table_type="demo"):
    print(record["primaryid"], record["sex"], record["age"])
```

---

## 🧪 Testing & Quality

```bash
# Run test suite
uv run --extra dev pytest tests/ -v

# Run type checks
uv run --extra dev pyrefly check src/ tests/
uv run --extra dev mypy src/ tests/

# Run linter
uv run --extra dev ruff check .
```

---

## 👥 Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/prateek-dagar"><img src="https://avatars.githubusercontent.com/u/107306613?v=4" width="100px;" alt="Prateek Dagar"/><br /><sub><b>Prateek Dagar</b></sub></a><br /><a href="https://github.com/raxtik-org/raxtik-source-faers/commits?author=prateek-dagar" title="Code">💻</a> <a href="https://github.com/raxtik-org/raxtik-source-faers/commits?author=prateek-dagar" title="Documentation">📖</a> <a href="#infra-prateek-dagar" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="#maintenance-prateek-dagar" title="Maintenance">🚧</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

---

## 📄 License
Licensed under the [GNU Affero General Public License v3.0 (AGPL-3.0)](./LICENSE).
