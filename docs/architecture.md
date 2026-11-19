# Architecture & Schema Signatures

`raxtik-source-faers` implements the `SourceAdapter` protocol, isolating all FDA-specific archive layouts, ASCII file anomalies, and historical schema evolution from the canonical `raxtik-etl` engine.

---

## 🏛️ Decoupled Plugin Architecture

```mermaid
graph TD
    subgraph FDA ["FDA Data Archives (2004-2026)"]
        A1["Legacy AERS (2004Q1-2012Q3)<br/>S1 Signature"]
        A2["Early FAERS (2012Q4-2014Q2)<br/>S2 Signature"]
        A3["Modern FAERS (2014Q3-Present)<br/>S3 Signature"]
    end

    subgraph SourceAdapter ["raxtik-source-faers"]
        B1["QuarterlyArchiveFetcher<br/>Dual-era URL discovery & failover"]
        B2["SignatureResolver<br/>Header inspection & schema classification"]
        B3["ASCII Parser & Stager<br/>Delimiter handling & quote escaping"]
        B4["Historical Column Mapper<br/>Normalizes S1/S2/S3 into canonical layout"]
        B5["Reference Code Sets<br/>CDER routes, forms, outcomes, ISO countries"]
    end

    subgraph CoreEngine ["raxtik-etl Engine"]
        C1["Validation & Deduplication"]
        C2["Deterministic Case Resolution"]
        C3["Packaging (DuckDB & Parquet)"]
    end

    FDA --> B1
    B1 --> B2
    B2 --> B3
    B3 --> B4
    B4 --> C1
    B5 --> C1
    C1 --> C2
    C2 --> C3
```

---

## 🔍 Historical FDA Signatures (Fail-Closed)

Over the past 22 years, the FDA has modified ASCII archive structures, table delimiters, and primary key conventions across three distinct eras:

| Era | Signature | Temporal Coverage | Delimiter | Primary Key Column | Case Identifier |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Legacy AERS** | **`S1`** | 2004Q1 – 2012Q3 | `$` / comma | `isr` | `case` |
| **Early FAERS** | **`S2`** | 2012Q4 – 2014Q2 | `$` | `primaryid` | `caseid` |
| **Modern FAERS** | **`S3`** | 2014Q3 – Present | `$` | `primaryid` | `caseid` |

### Fail-Closed Validation
The parser inspects the header row of all 7 raw ASCII files before processing:
- If all expected columns match a recognized signature (`S1`, `S2`, or `S3`), extraction proceeds using the appropriate schema mapper.
- If any required column is missing, or if an unrecognized column layout is detected, the adapter raises an immediate `ValueError` and halts execution. Corrupted or unverified data is never loaded into the pipeline.

---

## 🛠️ Handling ASCII Quirks

1. **Embedded Delimiters**: Some drug brand names or indication descriptions contain embedded `$` characters. The parser utilizes regex-based field splitting aligned with the expected column count.
2. **Missing Demographic Links**: In multi-quarter surveillance updates, child records (`drug`, `reac`, `indi`, `ther`) occasionally reference a `primary_id` from a prior quarter. The adapter stages these records while reporting referential integrity counts.
3. **Date Standardization**: FDA date fields (`fda_dt`, `mfr_dt`, `start_dt`, `end_dt`) appear in varied formats (`YYYYMMDD`, `YYYYMM`, `YYYY`). The adapter normalizes all dates to ISO-8601 (`YYYY-MM-DD`).

