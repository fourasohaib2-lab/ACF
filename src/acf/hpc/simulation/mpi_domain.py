"""MPI distributed domain decomposition for HPC clusters."""

import numpy as np


class MPIDomainDecomposition:
    """Manages 2D/3D spatial domain decomposition for distributed computing.

    Divides global grid into local sub-domains with ghost/halo boundary exchanges.
    """

    def __init__(
        self,
        global_nlat: int,
        global_nlon: int,
        n_proc_lat: int = 2,
        n_proc_lon: int = 4,
        rank: int = 0,
    ) -> None:
        self.global_nlat = global_nlat
        self.global_nlon = global_nlon
        self.n_proc_lat = n_proc_lat
        self.n_proc_lon = n_proc_lon
        self.rank = rank

        self.total_procs = n_proc_lat * n_proc_lon
        self.rank_lat = rank // n_proc_lon
        self.rank_lon = rank % n_proc_lon

        self.local_nlat = global_nlat // n_proc_lat
        self.local_nlon = global_nlon // n_proc_lon

    def get_local_bounds(self) -> tuple[int, int, int, int]:
        """Return (lat_start, lat_end, lon_start, lon_end) index bounds for local process."""
        lat_start = self.rank_lat * self.local_nlat
        lat_end = lat_start + self.local_nlat
        lon_start = self.rank_lon * self.local_nlon
        lon_end = lon_start + self.local_nlon

        return lat_start, lat_end, lon_start, lon_end

    def exchange_halo_boundaries(self, local_array: np.ndarray, halo_width: int = 1) -> np.ndarray:
        """
        Exchange ghost cell boundaries with neighboring ranks (halo update).

        NOTE (correction): this used to silently return
        local_array.copy() - a no-op that never touched the halo/
        ghost rows or columns and never communicated with any other
        rank - while its docstring and name claimed a real halo
        exchange. Unlike the status-dict fabrications elsewhere in
        this package, this one sits inside actual numerical simulation
        code: a caller running a genuinely distributed simulation
        across multiple ranks would silently get wrong (stale/
        uninitialized) values at every domain boundary, with no error
        raised. No MPI library is imported or initialized anywhere in
        this codebase (same underlying gap as
        hpc.mpi_solver.MPIEarthDomainSolver and
        hpc.distributed_grid.DistributedGridTopology, both already
        fixed), so a real exchange cannot be performed here - raising
        is the honest behavior instead of returning silently-wrong
        data. Currently unused elsewhere in the codebase and untested,
        confirmed via search.
        """
        raise NotImplementedError(
            "exchange_halo_boundaries: no MPI library is connected in this codebase - "
            "cannot perform a real inter-rank halo exchange. "
            "Returning local_array unchanged would silently produce wrong boundary values."
        )
