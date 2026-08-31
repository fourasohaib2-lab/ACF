# RELEASE SPECIFICATION — ACF v0.3

**Milestone:** EPyGrAM Reader & Ingestion Pipeline Integration  
**Target Release Date:** Sprint 1  
**Maturity Goal:** Production for FA/LFA/LFI Ingestion  

---

## 1. Objectives & Scope
- **Scientific Goal**: Seamless ingestion of Météo-France spectral/grid binary formats (AROME, ARPEGE, ALADIN).
- **Engineering Goal**: Establish canonical `EPyGrAMReader` in `src/acf/data/readers/epygram_reader.py` with zero breaking changes to existing GRIB or NetCDF readers.
- **Entry Criteria**: ACF v0.2 codebase clean compilation and test pass.
- **Exit Criteria**: `tests/test_epygram_reader.py` 100% pass (11/11 tests).
