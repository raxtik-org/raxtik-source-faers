# raxtik-source-faers

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

Or for local development:
```bash
pip install -e /path/to/raxtik-source-faers
```

Once installed, the connector is automatically discovered by `raxtik-etl` via Python entry-points:
```toml
[project.entry-points."raxtik_etl.sources"]
faers = "raxtik_source_faers.adapter:FAERSAdapter"
```

---

## 🚀 Usage

### Via `raxtik-etl` CLI
```bash
# Build a standalone package using the faers connector
raxtik-etl build-package --source faers --release 2004Q1 --zip-path /path/to/2004q1_ascii.zip
```

### Programmatic Usage
```python
import duckdb
from pathlib import Path
from raxtik_etl.sources.protocol import SourceArtifact
from raxtik_source_faers.adapter import FAERSAdapter

con = duckdb.connect("my_database.duckdb")
adapter = FAERSAdapter()

artifact = SourceArtifact(
    path=Path("data/raw/archives_cache/2004q1_ascii.zip"),
    release="2004Q1"
)

result = adapter.extract_and_load(con, artifact)
print(f"Extracted {result.row_counts['demo']} reports under signature {result.signature_id}")
```

---

## 🧪 Testing

```bash
pytest tests/ -v
```

Tests cover:
- S1, S2, and S3 signature detection.
- Fail-closed assertions on unrecognized schemas or missing tables.
- End-to-end extraction into DuckDB and canonical table counts.

---

## 📄 License
Licensed under the [GNU Affero General Public License v3.0 (AGPL-3.0)](./LICENSE).
