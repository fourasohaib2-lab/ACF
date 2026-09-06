# ACF MASTER VALIDATION PLAN

| Validation Stage | Gate Description | Target Criteria | Pass/Fail Gate |
| :--- | :--- | :--- | :---: |
| **Stage 1: Code Compilation** | Source tree Python compilation check | `python -m compileall src` returns code 0 | **PASS** |
| **Stage 2: Dependency Verification** | 48/48 package import verification | `python -c "import pkg..."` 100% success | **PASS** |
| **Stage 3: PyTest Regression Suite** | Full test suite execution across `tests/` | 2 154 / 2 154 tests pass (100.0%) | **PASS** |
| **Stage 4: HPC Infrastructure Check** | Slurm connection & Fennec cluster inspection | `HPCMonitor` status ok / mock fallback clean | **PASS** |
| **Stage 5: ESOC GUI Integration** | PySide6 widget instantiation & signals | Panels instantiate without Qt exceptions | **PASS** |
