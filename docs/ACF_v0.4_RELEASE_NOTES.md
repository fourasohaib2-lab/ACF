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

# ACF v0.4 RELEASE NOTES

**Release Version:** v0.4.0  
**Release Date:** August 6, 2026  

---

## 🚀 Key Highlights & New Capabilities

1. **EPyGrAM FA/LFA/LFI Reader Backend (`EPyGrAMReader`)**:
   - Direct ingestion of Météo-France AROME, ARPEGE, and ALADIN binary spectral and grid fields into canonical `Dataset` objects.
2. **Slurm HPC Monitoring Engine (`HPCMonitor`)**:
   - Live inspection of `squeue`, `sacct`, `sinfo`, and `scontrol` with automatic cluster health scoring.
3. **ESOC Operations Center HPCDashboardPanel**:
   - PySide6 interactive dashboard featuring live queue stats, cluster node health, and JSON exports.
