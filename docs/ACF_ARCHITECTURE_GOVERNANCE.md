# ACF ARCHITECTURE GOVERNANCE (ACF-G001)

## 1. ARCHITECTURE REVIEW BOARD (ARB) & COMPLIANCE

- **Ownership**: The Lead Systems Engineer holds ultimate authority over package hierarchy (`src/acf/data/`, `src/acf/models/`, `src/acf/hpc_connector/`, `src/acf/gui/esoc/`, `src/acf/master/`).
- **Zero Breaking Change Policy**: Modifying existing public function signatures or class contracts requires ARB review and an approved RFC.
- **Module Maturity Manifest**: Every component must maintain a valid `module.yaml` manifest tracked by `ModuleRegistryManager`.
