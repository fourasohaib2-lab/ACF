# APPENDIX D — DEPENDENCY MATRIX (ACF-MISSION-001A)

| Subsystem | Core Python Dependencies | External C/Fortran Libraries | System Dependencies |
| :--- | :--- | :--- | :--- |
| **`acf.data`** | `numpy`, `pandas`, `xarray`, `netCDF4`, `h5py`, `zarr` | `eccodes`, `epygram` (bronx/footprints) | `libeccodes.so`, `libnetcdf.so` |
| **`acf.models`** | `pydantic`, `pyyaml` | Slurm C API (`sbatch`, `squeue`, `sacct`) | Slurm Workload Manager |
| **`acf.hpc_connector`**| `paramiko`, `rich`, `click`, `typer` | OpenMPI (`mpirun`, `mpicc`) | OpenMPI 4.1+, SSH daemon |
| **`acf.gui.esoc`** | `PySide6`, `matplotlib`, `cartopy` | Qt 6.11.1 C++ Runtime | X11 / Wayland, OpenGL drivers |
| **`acf.verification`** | `scipy`, `scikit-learn` | BLAS / LAPACK | CPython 3.12+ |
