# Contributing to raxtik-source-faers

Thank you for your interest in contributing to **raxtik-source-faers**! We welcome bug reports, feature suggestions, documentation improvements, and code contributions.

---

## 🛠️ Development Setup

The project uses modular requirement files matching the Watchdog architecture:
* `requirements-lint.txt` - Code style, spelling, and static typing (Ruff, Typos, Pyrefly)
* `requirements-docs.txt` - Sphinx documentation and Read the Docs dependencies
* `requirements-tests.txt` - Automated testing and test coverage
* `requirements-dev.txt` - All development dependencies combined

```bash
# Clone the repository
git clone https://github.com/raxtik-org/raxtik-source-faers.git
cd raxtik-source-faers

# Create virtualenv and install full development suite
uv venv --python 3.13
source .venv/bin/activate
uv pip install -e ../raxtik-etl -e ".[dev,docs]" -r requirements-dev.txt
```

---

## 🧪 Testing

Run the full automated test suite with `pytest`:

```bash
uv run pytest tests/ -v
```

Or run via `tox`:
```bash
tox -e py313
```

---

## 🧹 Code Quality & Formatting

```bash
# Lint and format with Ruff
uv run ruff check --fix .
uv run ruff format .

# Check for spelling errors with Typos
uv run typos

# Run Pyrefly static type checking
uv run pyrefly check src/raxtik_source_faers
```

---

## 📚 Building Documentation

Documentation is built with Sphinx:

```bash
uv run --extra docs sphinx-build -b html docs docs/_build/html
```
