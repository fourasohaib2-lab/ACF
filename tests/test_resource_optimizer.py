"""
Unit test suite for HPCResourceOptimizer (ACF-HPC-004).
"""

from acf.hpc_connector.resource_optimizer import HPCResourceOptimizer


def test_estimate_resources():
    """Test resource estimation for different NWP models."""
    res_arome = HPCResourceOptimizer.estimate_resources("AROME", {"grid_points": 1000000, "forecast_hours": 48})
    assert res_arome["model_name"] == "AROME"
    assert res_arome["nodes"] >= 1
    assert res_arome["partition"] == "Researches"

    res_arpege = HPCResourceOptimizer.estimate_resources("ARPEGE", {"grid_points": 2000000, "forecast_hours": 72})
    assert res_arpege["nodes"] >= 2


def test_generate_slurm_script():
    """Test generating Slurm script."""
    script = HPCResourceOptimizer.generate_slurm_script("ALADIN", {"grid_points": 500000})
    assert "#SBATCH --job-name=acf_aladin" in script
    assert "#SBATCH --partition=Researches" in script
    assert "mpirun" in script
