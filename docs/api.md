# API Reference

Complete Python API documentation for `raxtik-source-faers`.

---

## 🏛️ `FAERS` Client

```{eval-rst}
.. autoclass:: raxtik_source_faers.client.FAERS
   :members:
   :inherited-members:
   :undoc-members:
   :show-inheritance:
```

> **Note**: `FAERS` inherits all dataset exploration and query methods (`cases()`, `drugs()`, `reactions()`, `outcomes()`, `indications()`, `therapies()`, `query()`, `print_summary()`) from [`raxtik_etl.BaseDataset`](https://raxtik-etl.readthedocs.io/en/latest/api.html#sdk-client).

---

## 🔌 `FAERSAdapter`

```{eval-rst}
.. autoclass:: raxtik_source_faers.adapter.FAERSAdapter
   :members:
   :undoc-members:
```

---

## 🌐 Archive Fetcher

```{eval-rst}
.. autofunction:: raxtik_source_faers.fetcher.download_quarterly_archive
```

