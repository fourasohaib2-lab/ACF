"""
Distributed Grid Topology & Halo Exchange Module
"""

from typing import Any


class DistributedGridTopology:
    """Gestionnaire de la topologie de grille distribuée et d'échange de mailles fantômes (Halo Exchange)."""

    @classmethod
    def exchange_halos(cls) -> dict[str, Any]:
        """
        NOTE (correction): this used to unconditionally claim
        "HALO_EXCHANGE_COMPLETE" with a fixed "0.12ms" communication
        time, with 0 parameters and no real distributed run connected
        - same underlying issue as hpc.mpi_solver.MPIEarthDomainSolver
        (also fixed, in the same package): no MPI library is imported
        or initialized anywhere in this codebase. Not fabricated.
        """
        return {
            "halo_depth": 2,
            "communication_time_ms": None,
            "status": "NOT_EXCHANGED_NO_MPI_LIBRARY_CONNECTED",
            "is_real_data": False,
        }
