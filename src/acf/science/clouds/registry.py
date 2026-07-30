"""
Atmospheric Complexity Framework (ACF)

Cloud Scientific Registry
"""

from typing import Any, Dict, List, Optional
from acf.science.clouds.base import CloudProcess


class CloudScientificRegistry:
    """
    Registre centralisé des lois et processus physiques des nuages.
    """

    _processes: Dict[str, CloudProcess] = {}
    _initialized: bool = False

    @classmethod
    def _ensure_initialized(cls):
        if cls._initialized:
            return
        cls._initialized = True
        # Lazy import of engines to trigger registration of processes
        from acf.science.clouds.microphysics import CloudMicrophysicsEngine
        from acf.science.clouds.thermodynamics import CloudThermodynamicsEngine
        from acf.science.clouds.dynamics import CloudDynamicsEngine
        from acf.science.clouds.radiation import CloudRadiationEngine
        from acf.science.clouds.aerosols import CloudAerosolEngine

        CloudMicrophysicsEngine()
        CloudThermodynamicsEngine()
        CloudDynamicsEngine()
        CloudRadiationEngine()
        CloudAerosolEngine()

    @classmethod
    def register(cls, process: CloudProcess):
        """
        Enregistre un processus nuageux dans le registre.
        """
        cls._processes[process.key] = process

    @classmethod
    def get(cls, key_or_name: str) -> Optional[CloudProcess]:
        """
        Récupère un processus nuageux par sa clé ou son nom.
        """
        cls._ensure_initialized()
        if key_or_name in cls._processes:
            return cls._processes[key_or_name]
        query = key_or_name.lower()
        for proc in cls._processes.values():
            if proc.name.lower() == query or proc.key.lower() == query:
                return proc
        return None

    @classmethod
    def search(cls, query: str) -> List[CloudProcess]:
        """
        Recherche des processus nuageux par mot-clé.
        """
        cls._ensure_initialized()
        q = query.lower()
        results = []
        for proc in cls._processes.values():
            text = f"{proc.name} {proc.domain} {proc.description} {proc.equation}".lower()
            if q in text:
                results.append(proc)
        return results

    @classmethod
    def list_processes(cls, domain: Optional[str] = None) -> List[CloudProcess]:
        """
        Liste tous les processus nuageux enregistrés.
        """
        cls._ensure_initialized()
        if domain is None:
            return list(cls._processes.values())
        dom_lower = domain.lower()
        return [p for p in cls._processes.values() if dom_lower in p.domain.lower()]

    @classmethod
    def calculate(cls, process_key: str, **kwargs) -> Any:
        """
        Évalue directement un processus nuageux par sa clé.
        """
        cls._ensure_initialized()
        proc = cls.get(process_key)
        if proc is None:
            raise KeyError(f"Processus nuageux inconnu: '{process_key}'")
        return proc.calculate(**kwargs)

    @classmethod
    def count(cls) -> int:
        """
        Retourne le nombre total de processus enregistrés.
        """
        cls._ensure_initialized()
        return len(cls._processes)


CloudRegistry = CloudScientificRegistry
