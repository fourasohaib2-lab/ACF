# ACF QUALITY MANAGEMENT PLAN (ACF-G001)

## 1. QUALITY OBJECTIVES & GATES

- **Test Pass Target**: 100% test pass rate across `pytest tests/` (Currently **2 154 / 2 154 tests pass**).
- **Compilation Gate**: `python -m compileall src` must exit code 0 before tagging any release.
- **Scientific Gate**: Verification metrics (RMSE, BIAS, ACC) computed on every forecast release.
