# ATMOSPHERIC COMPLEXITY FRAMEWORK (ACF)
## UNIFIED EARTH SYSTEM OPERATIONS CENTER (ESOC)
### DEFAULT OPERATIONAL APPLICATION MIGRATION SPECIFICATION — ACF-UI-012

---

## 1. EXECUTIVE SUMMARY

Mission **ACF-UI-012: Make ESOC the Default Operational Application** establishes the **Unified Earth System Operations Center (ESOC)** as the official, primary startup interface for the Atmospheric Complexity Framework.

Executing `python -m acf.gui.app` now boots directly into `ESOCWindow`, exposing all 26+ scientific engineering domains, 19 dockable operational panels, 10 role-tailored workspace modes, 8 interactive view projections, 22 system explorer categories, and 7 inspector tabs.

---

## 2. STARTUP PIPELINE ARCHITECTURE

```
                      python -m acf.gui.app
                               │
                        QApplication(sys.argv)
                               │
                         ThemeManager()
                               │
                          SplashScreen()
                               │
                 ESOCWindow (src/acf/gui/esoc/esoc_window.py)
                               │
                          app.exec()
```

---

## 3. SUMMARY OF CONNECTED SUBSYSTEMS

The ESOC `ModuleRegistry` connects:
1. Earth Physics (`acf.earth_physics`)
2. Numerical Simulation Engine (`acf.simulation_engine`)
3. Weather Forecast Engine (`acf.forecast`)
4. Data Assimilation Framework (`acf.data_assimilation`)
5. Earth Digital Twin (`acf.digital_twin`)
6. Planetary Dashboard (`acf.digital_twin.planetary_dashboard`)
7. Extreme Hazard Operations (`acf.hazard_operations`)
8. Climate Scenarios (`acf.simulation_engine.climate_scenarios`)
9. Hydrodynamic Ocean & Waves (`acf.simulation_engine.ocean_solver`)
10. Soil & River Hydrology (`acf.hydrology`)
11. Cryosphere Physics (`acf.earth_physics.cryosphere_physics`)
12. Terrestrial & Ocean Carbon Cycle (`acf.earth_physics.carbon_cycle`)
13. Air Quality & Chemistry (`acf.science.encyclopedia.chemistry`)
14. Space Weather Platform (`acf.space_weather`)
15. Geology Platform (`acf.geology`)
16. Global Earth Monitoring (`acf.monitoring`)
17. Production Dashboard (`acf.gui.dashboard`)
18. AI Expert Systems (`acf.ai_expert`)
19. Geoengineering Experiment Lab (`acf.geoengineering`)
20. AI Forecast Intelligence (`acf.visualization.ai_forecast_center`)
21. HPC Computing & GPU Layer (`acf.hpc`)
22. Data Output Exporters (`acf.simulation_engine.output`)
23. Forecast Verification (`acf.verification`)
24. Data & Parameter Catalogs (`acf.catalog`)
25. Plugin Manager (`acf.plugins`)
26. Unified GUI Framework (`acf.gui.esoc`)

---

## 4. VERIFICATION STATUS

- Compilation (`python -m compileall src`): PASSED (0 errors).
- Linter (`ruff check src/acf/gui/esoc/`): PASSED (0 errors).
- Full Test Suite (`pytest -q`): PASSED (All 2091+ tests passed).
