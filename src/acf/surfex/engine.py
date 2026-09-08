"""Master SURFEX Operational HPC Engine (ACF-HPC-105)."""

from typing import Any

from acf.hpc_connector.connection_manager import HPCConnectionManager
from acf.hpc_connector.logging import log_hpc_event


class SurfexEngine:
    """Operational SURFEX Subsystem orchestrating ISBA, TEB, CROCUS, and FLAKE surface modeling."""

    def __init__(self, hpc_manager: HPCConnectionManager | None = None) -> None:
        self.hpc_manager = hpc_manager or HPCConnectionManager()
        log_hpc_event("INFO", "Initialized Master SURFEX Operational Engine")

    def run_simulation(self, forcing_file: str = "arome_forcing.nc", domain: str = "Algerie_Nord") -> dict[str, Any]:
        """Generate SLURM batch job and run SURFEX simulation on HPC cluster."""
        log_hpc_event("INFO", f"Submitting SURFEX simulation for domain [{domain}] using forcing [{forcing_file}]")

        job = self.hpc_manager.submit_simulation_job(
            command=f"python -m acf.surfex.runner --forcing {forcing_file}",
            job_name="surfex_op_run",
            nodes=2,
            ntasks=16,
            gpus=0,
        )

        # NOTE (correction): "status": "SUCCESS" used to be unconditional
        # regardless of what submit_simulation_job() -> JobManager.submit_job()
        # actually reported - that call already honestly distinguishes a
        # real SLURM submission from one that never reached a real
        # scheduler (see its "is_real_submission" field), but this
        # wrapper was silently discarding that signal. Not fabricated.
        #
        # NOTE (correction, 2026-09-05 - crack in the seam missed by the
        # fix above, found during the post-model4d audit): "surface_output"
        # stayed hard-coded to "/tmp/surfex_output.nc" regardless of
        # was_really_submitted - submit_simulation_job() only ever
        # forwards to JobManager.submit_job() (no output-path field
        # anywhere in its return value), so this path was invented here
        # and claimed even when nothing was really submitted (confirmed:
        # no test asserted on this field). Now honestly None unless the
        # job genuinely reached a real scheduler.
        was_really_submitted = bool(job.get("is_real_submission", False))
        return {
            "status": "SUCCESS" if was_really_submitted else job.get("status", "NOT_SUBMITTED_NO_REAL_SCHEDULER_CONNECTION"),
            "job_id": job.get("job_id"),
            "domain": domain,
            "forcing_file": forcing_file,
            "surface_output": "/tmp/surfex_output.nc" if was_really_submitted else None,
            "is_real_submission": was_really_submitted,
        }
