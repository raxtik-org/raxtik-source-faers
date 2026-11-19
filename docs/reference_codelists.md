# Reference Codelists

`raxtik-source-faers` embeds standard clinical lookup dimensions curated from official FDA CDER and ICH standards.

---

## 📋 Available Reference Sets

| Reference Set | Python Constant | Description | Standard Authority |
| :--- | :--- | :--- | :--- |
| **Administration Routes** | `FDA_ROUTE_REFERENCE` | Routes of administration (Oral, Intravenous, Topical...) | FDA CDER / FAERS QDE |
| **Dosage Forms** | `FDA_FORM_REFERENCE` | Pharmaceutical formulation types (Tablet, Capsule, Solution...) | FDA CDER / FAERS QDE |
| **Reporter Occupations** | `FDA_OCCP_REFERENCE` | Initial reporter qualifications (Physician, Pharmacist, Consumer...) | FDA CDER |
| **Outcomes & Seriousness** | `FDA_OUTC_REFERENCE` | Clinical outcome classifications (Death, Hospitalization, Disability...) | FDA CDER |
| **Report Sources** | `FDA_RPSR_REFERENCE` | Transmission channels (Direct, Expedited 15-day, Periodic...) | FDA CDER |
| **Life Stages** | `FDA_AGE_GROUP_REFERENCE` | ICH E2B age classifications (Neonate, Infant, Child, Adult, Elderly) | ICH E2B |
| **Country Codes** | `ICH_ISO_COUNTRIES_REFERENCE` | ISO 3166-1 alpha-2 country codes and country names | ISO / ICH |
| **Duration & Age Units** | `FDA_TIME_UNITS_REFERENCE` | Normalized time and duration unit mappings | FDA CDER |

---

## 💻 Accessing Reference Sets in Python

```python
from raxtik_source_faers.reference import (
    FDA_FORM_REFERENCE,
    FDA_OUTC_REFERENCE,
    FDA_ROUTE_REFERENCE,
    ICH_ISO_COUNTRIES_REFERENCE,
)

# Inspect standard outcomes
for entry in FDA_OUTC_REFERENCE:
    print(f"{entry.code}: {entry.name} ({entry.description})")
```

When packaging quarterly DuckDB files, these reference dimensions are embedded as dedicated `_code_*` lookup tables (e.g. `_code_route`, `_code_outc`, `_code_country`) for in-database joins.

