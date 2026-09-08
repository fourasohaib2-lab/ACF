# PIPELINE D'EXÉCUTION HPC PAS-A-PAS (ACF-HPC-001)

**Role :** Chief HPC Architect & Chief Distributed Systems Architect  
**Date :** 3 août 2026  
**Dépôt :** Atmospheric Complexity Framework (ACF)  

---

## 1. Description du Pipeline d'Exécution HPC (11 Étapes)

```
[1. Connexion SSH]
       │
       ▼
[2. Validation Environnement]
       │
       ▼
[3. Transfert / Staging Données]
       │
       ▼
[4. Prétraitement & Configuration]
       │
       ▼
[5. Soumission Job (SLURM/PBS)]
       │
       ▼
[6. Surveillance & Heartbeat]
       │
       ▼
[7. Collecte des Résultats]
       │
       ▼
[8. Post-Traitement & Conversion]
       │
       ▼
[9. Archivage Sécurisé]
       │
       ▼
[10. Visualisation ESOC / MapEngine]
       │
       ▼
[11. Nettoyage Automatique]
```

### Détail des Étapes :
1. **Connexion SSH** : Établissement d'une connexion persistance via `ConnectionManager`.
2. **Validation Environnement** : Vérification des modules HPC (`eccodes`, `netcdf`, `epygram`, `openmpi`) via `EnvironmentManager`.
3. **Transfert Données** : Staging des fichiers d'entrée via `FileTransfer` (SFTP/rsync).
4. **Prétraitement** : Génération des namelists et préparation du script batch SLURM.
5. **Soumission Job** : Transmission de la commande `sbatch` via `JobManager`.
6. **Surveillance** : Polling périodique et écoute du statut (`squeue` / `qstat`) via `WorkflowMonitor`.
7. **Collecte Résultats** : Rapatriement des fichiers de sortie FA/GRIB2 vers le stockage local/réseau.
8. **Post-Traitement** : Ingestion via `UniversalDataIngestionEngine` et conversion `Dataset`.
9. **Archivage** : Sauvegarde des sorties certifiées via `WorkflowArchive`.
10. **Visualisation** : Rendu cartographique temps-réel sur le canvas `MapEngine` / `ESOC`.
11. **Nettoyage Automatique** : Effacement des fichiers temporaires distants et libération des ressources.
