# SPÉCIFICATION DE L'INTERFACE CANONIQUE DES MODÈLES NWP ACF (ACF-NWP-001)

**Role :** Chief NWP Architect & Chief Software Architect  
**Date :** 3 août 2026  
**Dépôt :** Atmospheric Complexity Framework (ACF)  

---

## 1. Contrat d'Interface `BaseWeatherModel` (`src/acf/models/base_model.py`)

Tous les modèles de prévision numérique du temps (Météo-France, ECMWF, NOAA, DWD, NCAR) implémentent le contrat standardisé `BaseWeatherModel` offrant un cycle de vie unifié en 10 étapes :

```python
class BaseWeatherModel(ABC):
    """Interface d'exécution et d'ingestion abstraite commune pour tous les modèles NWP."""

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialise les paramètres d'exécution du modèle."""
        pass

    @abstractmethod
    def configure(self, cycle: str, domain: str) -> None:
        """Configure le cycle réseau (00Z-18Z) et le domaine d'intégration."""
        pass

    @abstractmethod
    def prepare_input(self, dataset: Dataset) -> bool:
        """Prépare les fichiers de conditions aux limites et initiales."""
        pass

    @abstractmethod
    def run(self) -> Dict[str, Any]:
        """Lance l'exécution du noyau dynamique du modèle."""
        pass

    @abstractmethod
    def monitor(self) -> Dict[str, Any]:
        """Surveille l'avancement et la convergence du run."""
        pass

    @abstractmethod
    def postprocess(self) -> Dataset:
        """Exécute le post-traitement et convertit les sorties en Dataset ACF."""
        pass

    @abstractmethod
    def export(self, target_format: str) -> Path:
        """Exporte les résultats dans le format cible (GRIB2, NetCDF, FA)."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Ferme les ressources et nettoie les répertoires temporaires."""
        pass

    @abstractmethod
    def status(self) -> str:
        """Retourne le statut courant du modèle (IDLE, RUNNING, COMPLETED, FAILED)."""
        pass
```
