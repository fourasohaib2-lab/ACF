# ACF SOFTWARE GOVERNANCE (ACF-G001)

## 1. PYTHON CODING & QUALITY STANDARDS

- **Python Version**: CPython 3.12+ in `.venv`.
- **Type Annotations**: Mandatory type hints for all public functions (`from __future__ import annotations`).
- **Formatter & Linter**: Strict compliance with `ruff` and `black`.
- **Zero Syntax Errors**: `.venv/bin/python -m compileall src` must return code 0 on all commits.
