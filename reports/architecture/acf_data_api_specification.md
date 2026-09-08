# SPÉCIFICATION DE L'API CANONIQUE DES LECTEURS DE DONNÉES ACF (ACF-DATA-001)

**Role :** Chief Software Architect & Principal Python Architect  
**Date :** 3 août 2026  
**Dépôt :** Atmospheric Complexity Framework (ACF)  

---

## 1. Interface Canonique `BaseReader` (`src/acf/importers/base/base_reader.py`)

Tous les lecteurs spécialisés d'ACF implémentent l'interface standardisée `BaseReader` et fournissent un ensemble cohérent de méthodes métier :

```python
class BaseReader(ABC):
    """Interface d'ingestion abstraite commune pour tous les lecteurs ACF."""

    @abstractmethod
    def can_read(self, filename: str | Path) -> bool:
        """Vérifie si le fichier donné peut être lu par ce lecteur."""
        pass

    @abstractmethod
    def open(self, filepath: Optional[str | Path] = None) -> BaseReader:
        """Ouvre la ressource de données et initialise le lecteur."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Ferme la ressource de données et libère les handles système."""
        pass

    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """Extrait les métadonnées globales (format, centre, modèle, validité)."""
        pass

    @abstractmethod
    def geometry(self) -> Dict[str, Any]:
        """Extrait les caractéristiques géométriques et la grille spatiale."""
        pass

    @abstractmethod
    def projection(self) -> str:
        """Extrait le système de référence ou la projection cartographique."""
        pass

    @abstractmethod
    def domain(self) -> Dict[str, Any]:
        """Extrait la délimitation géographique (bounding box et résolutions)."""
        pass

    @abstractmethod
    def list_fields(self) -> List[str]:
        """Liste les noms ou identifiants des champs physiques disponibles."""
        pass

    @abstractmethod
    def read_field(self, field_id: str) -> Dict[str, Any]:
        """Lit un champ spécifique et renvoie ses données brutes et statistiques."""
        pass

    @abstractmethod
    def read_fields(self, field_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Lit une liste de champs par lot."""
        pass

    @abstractmethod
    def vertical_levels(self) -> List[Dict[str, Any]]:
        """Extrait la définition des niveaux verticaux (pression / hybrides)."""
        pass

    @abstractmethod
    def time_validity(self) -> Dict[str, Any]:
        """Extrait l'horodatage du réseau (basis time) et l'échéance valid time."""
        pass

    @abstractmethod
    def read(self, filename: str | Path) -> Dict[str, Any]:
        """Ouvre le fichier et renvoie un dictionnaire structuré complet."""
        pass
```

---

## 2. Spécification de l'Objet `Dataset` (`src/acf/data/dataset.py`)

Tout processus d'ingestion `UniversalDataIngestionEngine.ingest()` garantit la restitution d'une instance unique `acf.data.Dataset` enrichie des attributs ci-dessous :

- **`variables`** : Dictionnaire des variables physiques ingestées.
- **`dimensions`** : Dictionnaire des dimensions canoniques (`lat`, `lon`, `time`, `level`).
- **`metadata` / `attributes`** : Dictionnaires de métadonnées globaux.
- **`validated` & `errors`** : Statut du contrôle qualité automatique.
- **`created` & `modified`** : Horodatages ISO de suivi.
