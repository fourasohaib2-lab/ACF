# ACF Development Guide

## Environment Setup
ACF requires Python 3.12 or higher.

```bash
git clone https://github.com/meteo-dz/ACF.git
cd ACF
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Running Static Checks and Tests
```bash
# Pytest unit tests
pytest -v

# Code quality and style linting
ruff check .

# Static type checking
mypy src

# Documentation build
python3 scripts/generate_docs.py
```

## Scientific Conventions
- SI units are strictly required throughout all core calculation pipelines.
- Standard atmospheric constants are defined in `acf.core.constants`.
- All public APIs must provide explicit type hints and comprehensive docstrings.
