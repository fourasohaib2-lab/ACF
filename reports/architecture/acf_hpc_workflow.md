# SPÉCIFICATION DU WORKFLOW ENGINE OPERATOIRE HPC (ACF-HPC-001)

**Role :** Chief HPC Architect & Chief Scientific Computing Architect  
**Date :** 3 août 2026  
**Dépôt :** Atmospheric Complexity Framework (ACF)  

---

## 1. Cycles et Enums du Workflow Operational

Le `WorkflowEngine` orchestre les 4 cycles quotidiens de prévision météorologique :
- `UTC_00` : Cycle 00:00 UTC
- `UTC_06` : Cycle 06:00 UTC
- `UTC_12` : Cycle 12:00 UTC
- `UTC_18` : Cycle 18:00 UTC

---

## 2. Déroulement des 12 Operational Stages

```
 1. INITIALIZATION ──────►  2. PREPROCESSING ──────►  3. OBSERVATION_CHECK
                                                             │
 6. PREP ───────────────◄  5. SURFEX ─────────────◄  4. ASSIMILATION
    │
    ▼
 7. MODEL_RUN ──────────►  8. POST_PROCESSING ────►  9. PRODUCT_GENERATION
                                                             │
 12. CLEANUP ───────────◄  11. ARCHIVING ─────────◄  10. QUALITY_CONTROL
```

1. **INITIALIZATION** : Chargement de la configuration, création du contexte `CycleContext`.
2. **PREPROCESSING** : Préparation des fichiers d'entrée et grilles spatiales.
3. **OBSERVATION_CHECK** : Contrôle de disponibilité et qualité des observations BUFR.
4. **ASSIMILATION** : Exécution de l'assimilation de données (3D-Var / 4D-Var).
5. **SURFEX** : Préparation et calcul des bilans de surface (ISBA, TEB, FLake).
6. **PREP** : Génération des conditions aux limites et initiales.
7. **MODEL_RUN** : Exécution du noyau dynamique du modèle (AROME / ALADIN / ARPEGE).
8. **POST_PROCESSING** : Extraction des diagnostics physiques et conversion de formats.
9. **PRODUCT_GENERATION** : Génération des cartes et produits de prévision.
10. **QUALITY_CONTROL** : Contrôle qualité automatique des sorties.
11. **ARCHIVING** : Archivage sécurisé sur stockage capacitif.
12. **CLEANUP** : Nettoyage automatique des répertoires temporaires de calcul.
