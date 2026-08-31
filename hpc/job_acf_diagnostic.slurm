#!/bin/bash
#SBATCH --job-name=acf_hpc_diag
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --partition=gpu
#SBATCH --time=02:00:00
#SBATCH --output=/onm/dem/home/sfoura/ACF/logs/%j.out
#SBATCH --error=/onm/dem/home/sfoura/ACF/logs/%j.err

module purge
module load Python/3.11.5
export PYTHON_EXECUTABLE="/home/souhaib/ACF/.venv/bin/python"

srun /home/souhaib/ACF/.venv/bin/python -c "
import os, sys, platform
print('='*60)
print('PYTHON DIAGNOSTIC')
print('='*60)
print('Executable :', sys.executable)
print('Version    :', sys.version)
print('Platform   :', platform.platform())
print('Prefix     :', sys.prefix)
print('BasePrefix :', sys.base_prefix)

for lib in ['numpy', 'scipy', 'xarray', 'netCDF4', 'acf']:
    try:
        mod = __import__(lib)
        print(f'{lib:12s} :', getattr(mod, '__version__', 'Installed'))
    except Exception as e:
        print(f'{lib:12s} : Not Installed ({e})')

print('='*60)
print('ACF HPC READY')
"
