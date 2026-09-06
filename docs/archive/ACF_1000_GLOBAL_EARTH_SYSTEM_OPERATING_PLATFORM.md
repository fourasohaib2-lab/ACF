# ACF-1000 — GLOBAL EARTH SYSTEM OPERATING PLATFORM (GESOP)

**Date :** 6 août 2026  
**Statut :** Spécification d'Ingénierie Globale & Système de Maturité des Modules  
**Workspace Root :** `/home/souhaib/ACF` (obtenu via `git rev-parse --show-toplevel`)  
**Branche Git :** `develop`  

---

## 1. Vision et Architecture Globale GESOP

La plateforme opérationnelle globale d'ACF (**GESOP**) unifie l'ensemble des domaines du système Terre :
- Prévision Numérique du Temps (NWP) & Climat (CMIP6 / SSP)
- Océanographie & Vagues / Marées
- Hydrologie & Cycle de l'Eau
- Cryosphère & Biosphère / Carbone
- Chimie Atmosphérique, Qualité de l'Air & Poussières Désertiques (SURFEX / CHIMERE)
- Feux de Forêt, Énergie Renouvelable & Services Climatiques
- Système de Maturité des Modules (`module.yaml`)

---

## 2. Système de Maturité des Modules (`module.yaml` Manifest)

Chaque composant et module d'ACF intègre un manifeste de maturité `module.yaml` sous la responsabilité de `ModuleRegistryManager` (`src/acf/master/module_manifest.py`) :

```yaml
name: "hpc_connector"
owner: "Chief HPC Architect"
version: "2.1.0"
description: "Universal Slurm HPC Execution Connector & Monitoring Engine"
maturity: "Production" # Options: Prototype, Beta, Stable, Production
dependencies:
  - "acf.data"
  - "paramiko"
supported_models:
  - "ARPEGE"
  - "AROME"
  - "ALADIN"
  - "WRF"
  - "ICON"
  - "IFS"
test_coverage_pct: 100.0
doc_coverage_pct: 100.0
hpc_requirements:
  mpi: true
  openmp: true
  gpu: false
  slurm: true
```

### Niveaux de Maturité Exposés dans ESOC
1. **Prototype** : En cours d'exploration, fonctionnalités partielles.
2. **Beta** : Implémenté, tests unitaires partiels.
3. **Stable** : API stabilisée, couverture de tests > 80%.
4. **Production** : Intégration complète ESOC, compatibilité HPC, 100% de tests réussis.
