"""
HPC MPI Domain Decomposition & Parallel Solver Module
"""

from typing import Any


class MPIEarthDomainSolver:
    """Résolveur MPI distribuant la grille physique du système Terre sur plusieurs nœuds de calcul."""

    @classmethod
    def get_mpi_topology(cls, num_procs: int = 64) -> dict[str, Any]:
        """
        NOTE (correction): num_procs is genuinely echoed, but
        decomposition/communication_backend describe an intended
        design (kept, as a declared target) and "status":
        "MPI_TOPOLOGY_READY" claimed a real MPI communicator/topology
        had been set up - no MPI library (e.g. mpi4py) is imported or
        initialized anywhere in this codebase. Not fabricated.
        """
        return {
            "num_processes": num_procs,
            "planned_decomposition": "2D Latitude/Longitude Tile Decomposition",
            "planned_communication_backend": "OpenMPI 5.0 Non-blocking Halo Exchange",
            "status": "NOT_INITIALIZED_NO_MPI_LIBRARY_CONNECTED",
            "is_real_data": False,
        }
