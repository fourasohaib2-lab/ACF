# ACF CHANGELOG — RELEASE v0.4.0

All notable changes to the Atmospheric Complexity Framework for version 0.4.0 are documented below.

## [v0.4.0] - 2026-08-06

### Added
- Added `EPyGrAMReader` in `src/acf/data/readers/epygram_reader.py` for FA/LFA/LFI format support.
- Added `HPCMonitor` in `src/acf/hpc_connector/hpc_monitor.py` for Slurm cluster monitoring.
- Added `HPCDashboard` in `src/acf/hpc_connector/hpc_dashboard.py` for health score calculation.
- Added `HPCDashboardPanel` in `src/acf/gui/esoc/hpc_dashboard_panel.py` for ESOC operations UI.
- Added `tests/test_epygram_reader.py`, `tests/test_hpc_monitor.py`, and `tests/test_hpc_dashboard.py`.
