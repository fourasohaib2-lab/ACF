<!-- ACF_RECONCILIATION_BANNER_2026-09-02 -->
> **⚠️ Historical / unverified document.** This file was auto-generated as part
> of an earlier documentation sprint, and its completion, certification, or
> "100%"-style claims were not independently reproduced. For the actual,
> reproducible test/status numbers, see [`ROADMAP.md`](../ROADMAP.md) and
> [`README.md`](../README.md)'s "Verified Status" section; for what has
> genuinely been audited and fixed since, see
> [`ACF_PHYSICS_GUARD_AUDIT_CHANGELOG.md`](ACF_PHYSICS_GUARD_AUDIT_CHANGELOG.md).
> Treat any specific number, percentage, or "CERTIFIED"/"COMPLETE" claim below
> as aspirational unless it also appears in one of those documents.
>
> _Banner added 2026-09-02 per `ROADMAP.md`'s "reconcile ~150 certificate/
> sprint-report documents" near-term priority — original content preserved
> unchanged below._

---

# ACF SPRINT-001 TEST REPORT (ACF-EXEC-001)

| Test Case Name | Test File | Assertions Checked | Status |
| :--- | :--- | :--- | :---: |
| `test_epygram_reader_instantiation` | `tests/test_epygram_reader.py` | Valid class initialization & default attributes | **PASS** |
| `test_read_fa_file` | `tests/test_epygram_reader.py` | Spectral FA file parsing & Dataset returned | **PASS** |
| `test_read_lfa_file` | `tests/test_epygram_reader.py` | LFA format file parsing & grid conversion | **PASS** |
| `test_read_lfi_file` | `tests/test_epygram_reader.py` | SURFEX LFI format file parsing | **PASS** |
| `test_get_metadata` | `tests/test_epygram_reader.py` | Projection, levels, and grid dimensions | **PASS** |
| `test_get_available_fields` | `tests/test_epygram_reader.py` | Variable list extraction | **PASS** |
| `test_fallback_mode` | `tests/test_epygram_reader.py` | Binary fallback parser when epygram missing | **PASS** |
| **Total Test Suite** | `tests/test_epygram_reader.py` | **11 / 11 Tests Passed (100.0%)** | **PASS** |
