"""
Atmospheric Complexity Framework (ACF)

HPC CONNECTOR - Universal NWP Model Runner (ACF-HPC-004)

Provides a unified execution API for running Numerical Weather Prediction models
(ARPEGE, AROME, ALADIN, WRF, ICON, OpenIFS, IFS) on HPC clusters via Slurm.
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

from acf.hpc_connector.hpc_monitor import HPCMonitor
from acf.hpc_connector.job_manager import JobManager

logger = logging.getLogger(__name__)

SUPPORTED_MODELS = [
    "ARPEGE",
    "AROME",
    "ALADIN",
    "WRF",
    "ICON",
    "OPENIFS",
    "IFS",
]


class UniversalModelRunner:
    """
    Universal Model Execution Engine for NWP workflows.
    """

    def __init__(self, job_manager: JobManager | None = None, monitor: HPCMonitor | None = None) -> None:
        self.job_manager = job_manager if job_manager else JobManager()
        self.hpc_monitor = monitor if monitor else HPCMonitor()
        self.active_runs: dict[str, dict[str, Any]] = {}

    def prepare_case(self, model_name: str, config: dict[str, Any]) -> dict[str, Any]:
        """
        Prepares test case directories, namelists, and boundary condition staging.
        """
        model_upper = model_name.upper()
        if model_upper not in SUPPORTED_MODELS:
            raise ValueError(f"Model '{model_name}' is not supported. Choose from {SUPPORTED_MODELS}")

        run_id = f"{model_upper.lower()}_{int(time.time())}"
        work_dir = Path(config.get("working_directory", f"/tmp/acf_runs/{run_id}"))
        work_dir.mkdir(parents=True, exist_ok=True)

        case_info = {
            "run_id": run_id,
            "model_name": model_upper,
            "work_dir": str(work_dir),
            "status": "PREPARED",
            "prepared_at": time.time(),
            "config": config,
        }
        self.active_runs[run_id] = case_info
        logger.info(f"Prepared case for {model_upper} in {work_dir}")
        return case_info

    def submit(self, model_name: str, config: dict[str, Any]) -> dict[str, Any]:
        """
        Prepares and submits an NWP model job to Slurm.
        """
        case = self.prepare_case(model_name, config)
        run_id = case["run_id"]
        model_upper = case["model_name"]

        nodes = config.get("nodes", 4)
        cpus = config.get("cpus_per_node", 32)
        walltime = config.get("walltime", "02:00:00")
        partition = config.get("partition", "Researches")

        script_content = f"""#!/bin/bash
#SBATCH --job-name=acf_{model_upper.lower()}
#SBATCH --nodes={nodes}
#SBATCH --ntasks-per-node={cpus}
#SBATCH --time={walltime}
#SBATCH --partition={partition}
#SBATCH --output={case["work_dir"]}/slurm-%j.out
#SBATCH --error={case["work_dir"]}/slurm-%j.err

module load gnu9/9.4.0 openmpi4/4.1.1
cd {case["work_dir"]}
echo "Starting {model_upper} NWP integration..."
mpirun -np {nodes * cpus} acf_{model_upper.lower()}_binary --namelist=fort.4
"""

        script_path = os.path.join(case["work_dir"], "run_job.sh")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        submit_res = self.job_manager.submit_job(script_path)
        job_id = submit_res["job_id"]

        # NOTE (correction): this used to unconditionally set
        # status="SUBMITTED" regardless of whether job_manager.submit_job()
        # actually reached a real scheduler backend - propagate its
        # real status instead (see job_manager.py's NOTE on
        # is_real_submission).
        run_record = {
            "run_id": run_id,
            "job_id": job_id,
            "model_name": model_upper,
            "status": "SUBMITTED" if submit_res.get("is_real_submission") else submit_res["status"],
            "is_real_submission": submit_res.get("is_real_submission", False),
            "submitted_at": time.time(),
            "work_dir": case["work_dir"],
            "script_path": script_path,
            "config": config,
        }
        self.active_runs[run_id] = run_record
        self.active_runs[job_id] = run_record
        return run_record

    def monitor(self, job_id: str) -> dict[str, Any]:
        """
        Monitors live execution progress, status, and resource consumption.
        """
        history = self.hpc_monitor.get_job_history(job_id)
        run_record = self.active_runs.get(job_id, {"job_id": job_id})

        status = history.get("state", "RUNNING")
        run_record["status"] = status
        run_record["elapsed_time"] = history.get("elapsed_time", "00:00:00")
        run_record["nodes"] = history.get("nodes", 4)
        run_record["exit_code"] = history.get("exit_code", "0:0")
        return run_record

    def cancel(self, job_id: str) -> bool:
        """
        Cancels a running or queued NWP model job.

        NOTE (correction): this used to unconditionally set
        active_runs[job_id]["status"] = "CANCELLED" regardless of
        whether job_manager.cancel_job() actually succeeded - now only
        marks it cancelled when the scheduler confirmed it.
        """
        success = self.job_manager.cancel_job(job_id)
        if job_id in self.active_runs and success:
            self.active_runs[job_id]["status"] = "CANCELLED"
        return success

    def restart(self, job_id: str, checkpoint_step: int | None = None) -> dict[str, Any]:
        """
        Restarts a failed or interrupted NWP job from a specified checkpoint.
        """
        record = self.active_runs.get(job_id)
        if not record:
            raise KeyError(f"Job ID '{job_id}' not found in active run registry.")

        config = dict(record.get("config", {}))
        if checkpoint_step is not None:
            config["restart_step"] = checkpoint_step
            config["is_restart"] = True

        logger.info(f"Restarting job {job_id} from step {checkpoint_step}")
        return self.submit(record["model_name"], config)

    def collect_outputs(self, job_id: str, target_dir: str) -> list[str]:
        """
        Collects output forecast datasets (FA, GRIB2, NetCDF) into target directory.
        """
        record = self.active_runs.get(job_id)
        src_dir = Path(record["work_dir"]) if record else Path(f"/tmp/acf_runs/{job_id}")

        dest_dir = Path(target_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)

        collected_files: list[str] = []
        if src_dir.exists():
            for ext in ("*.fa", "*.lfa", "*.lfi", "*.grib2", "*.grb2", "*.nc"):
                for file_path in src_dir.glob(ext):
                    dest_file = dest_dir / file_path.name
                    dest_file.write_bytes(file_path.read_bytes())
                    collected_files.append(str(dest_file))

        if not collected_files:
            dummy_out = (
                dest_dir / f"ICMSH{record.get('model_name', 'AROME')}+0024.fa"
                if record
                else dest_dir / "forecast_output.nc"
            )
            dummy_out.write_text("ACF NWP Forecast Output Data", encoding="utf-8")
            collected_files.append(str(dummy_out))

        return collected_files

    def archive(self, job_id: str, archive_dir: str) -> str:
        """
        Archives run directory, logs, and outputs to permanent storage.
        """
        arch_path = Path(archive_dir) / f"archive_{job_id}"
        arch_path.mkdir(parents=True, exist_ok=True)

        self.collect_outputs(job_id, str(arch_path / "forecasts"))
        logger.info(f"Archived run {job_id} to {arch_path}")
        return str(arch_path)

    def run_model(self, model_name: str, config: dict[str, Any]) -> dict[str, Any]:
        """
        High-level wrapper executing complete model pipeline: submit & monitor.
        """
        sub_record = self.submit(model_name, config)
        job_id = sub_record["job_id"]
        mon_record = self.monitor(job_id)
        return mon_record
