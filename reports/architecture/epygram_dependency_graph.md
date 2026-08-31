# GRAPHE DE DÉPENDANCES ET D'INTÉGRATION EPYGRAM (ACF-ARCH-EPYGRAM-001)

**Role :** Principal Software Architect & Principal HPC Architect  
**Date :** 3 août 2026  
**Dépôt :** Atmospheric Complexity Framework (ACF)  

---

## 1. Graphe Global des Dépendances Composants

```mermaid
graph TD
    subgraph Formats Entrée
        F1[Fichiers FA *.fa]
        F2[Fichiers LFA *.lfa]
        F3[Fichiers GRIB *.grib2]
        F4[Fichiers NetCDF *.nc]
    end

    subgraph Bibliothèque Backend
        EPY[Bibliothèque EPyGrAM 2.1.0]
        FAL[falfilfa4py Fortran Bindings]
        ECC[ecCodes C/Fortran Library]
        EPY --> FAL
        EPY --> ECC
    end

    subgraph Couche Lecteurs ACF - src/acf/data/readers/
        R_EPY[EPyGrAMReader]
        R_GRIB[GRIBReader]
        R_NC[NetCDFReader]
        R_EPY --> EPY
    end

    subgraph Moteur d'Ingestion & Détection - src/acf/data/
        DET[FormatDetector]
        ING[UniversalDataIngestionEngine]
        DS[Objet Dataset]
        
        DET -->|Détecte FA/LFA| R_EPY
        ING --> DET
        ING --> R_EPY
        ING --> DS
    end

    subgraph Adaptateurs Modèles NWP - src/acf/models/
        ADP_ARP[ARPEGEIngestionAdapter]
        ADP_ARO[AROMEIngestionAdapter]
        ADP_ALA[ALADINIngestionAdapter]
        
        ADP_ARP --> R_EPY
        ADP_ARO --> R_EPY
        ADP_ALA --> R_EPY
    end

    subgraph Pipeline Métier & Workflows - src/acf/hpc_workflow/
        WF[WorkflowEngine]
        WF --> ADP_ARO
        WF --> ADP_ALA
        WF --> ADP_ARP
    end

    subgraph Exploitation & Visualisation
        VIS[MapEngine / AWCI Renderer]
        AI[Moteur IA & Prévision]
        ANA[Analyse & Diagnostics]
        
        DS --> VIS
        DS --> AI
        DS --> ANA
    end

    F1 --> DET
    F2 --> DET
    F3 --> DET
    F4 --> DET
```

---

## 2. Diagramme de Flux de Données Séquentiel

```mermaid
sequenceDiagram
    autonumber
    participant App as Application / Workflows
    participant Engine as UniversalDataIngestionEngine
    participant Detector as FormatDetector
    participant Reader as EPyGrAMReader
    participant Lib as epygram (Library)
    participant Dataset as Dataset Object

    App->>Engine: ingest(filepath)
    Engine->>Detector: detect(filepath)
    Detector-->>Engine: Retourne "FA" / "LFA"
    Engine->>Reader: open(filepath)
    Reader->>Lib: epygram.resources.open(filepath)
    Lib-->>Reader: Resource Handle
    Engine->>Reader: geometry(), metadata(), list_fields()
    Reader-->>Engine: Structured Grid & Meta Dicts
    Engine->>Dataset: Create Dataset & set_metadata()
    Engine-->>App: Dataset prêt pour l'analyse
```

---

## 3. Matrice de Isolation des Couches (Layer Isolation Rules)

| Couche Subsystem | Accès Direct à `epygram` ? | Interdiction Strict |
| :--- | :--- | :--- |
| `src/acf/data/readers/` | **OUI** (Seul point d'entrée officiel) | Ne doit pas dépendre de la GUI ou des solveurs |
| `src/acf/models/` | **OUI** (Via `EPyGrAMReader`) | Ne doit pas implémenter la logique binaire FA |
| `src/acf/hpc_workflow/` | **NON** (Via les adaptateurs modèles) | Ne doit pas importer directement `epygram` |
| `src/acf/gui/` | **STRICTEMENT NON** | Dépend uniquement des objets `Dataset` ou `MapEngine` |
| `src/acf/simulation_engine/` | **STRICTEMENT NON** | Indépendant des formats de fichiers physiques |
