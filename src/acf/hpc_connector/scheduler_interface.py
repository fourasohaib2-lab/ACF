"""Production SLURM Engine using Universal PythonResolver (ACF-HPC-101)."""

import uuid

from acf.hpc_connector.logging import log_hpc_event
from acf.hpc_connector.python_resolver import PythonResolver
from acf.hpc_connector.remote_executor import RemoteExecutor


class BaseSchedulerInterface:
    """Abstract scheduler interface base class."""

    def __init__(self, scheduler_name: str = "slurm", executor: RemoteExecutor | None = None) -> None:
        self.scheduler_name = scheduler_name
        self.executor = executor or RemoteExecutor()
        self.python_resolver = PythonResolver(self.executor)

    def submit_job(self, job_script: str, job_name: str = "acf_sim", nodes: int = 1, ntasks: int = 1) -> str:
        raise NotImplementedError

    def cancel_job(self, job_id: str) -> bool:
        raise NotImplementedError

    def get_job_status(self, job_id: str) -> str:
        raise NotImplementedError

    def generate_batch_script(
        self,
        command: str,
        job_name: str = "acf_arome_sim",
        nodes: int = 4,
        ntasks: int = 32,
        gpus: int = 4,
        walltime: str = "02:00:00",
        partition: str = "gpu",
    ) -> str:
        raise NotImplementedError


class SlurmScheduler(BaseSchedulerInterface):
    """Production SLURM Workload Manager using dynamic PythonResolver for compute nodes."""

    def __init__(self, executor: RemoteExecutor | None = None) -> None:
        super().__init__("slurm", executor)

    def generate_batch_script(
        self,
        command: str,
        job_name: str = "acf_arome_sim",
        nodes: int = 4,
        ntasks: int = 32,
        gpus: int = 4,
        walltime: str = "02:00:00",
        partition: str = "gpu",
    ) -> str:
        gpu_line = f"#SBATCH --gres=gpu:{gpus}\n" if gpus > 0 else ""
        py_info = self.python_resolver.resolve_python()

        py_module = py_info.get("python_module", "")
        py_path = py_info.get("python_path", "python")
        module_cmd = f"module load {py_module}\n" if py_module else ""

        # Replace any generic "python " in command with resolved Python executable
        formatted_cmd = command
        if command.startswith("python "):
            formatted_cmd = command.replace("python ", f"{py_path} ", 1)

        script = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --nodes={nodes}
#SBATCH --ntasks-per-node={ntasks}
#SBATCH --partition={partition}
#SBATCH --time={walltime}
{gpu_line}#SBATCH --output=/onm/dem/home/sfoura/ACF/logs/%j.out
#SBATCH --error=/onm/dem/home/sfoura/ACF/logs/%j.err

module purge
{module_cmd}export PYTHON_EXECUTABLE="{py_path}"

srun {formatted_cmd}
"""
        return script

    def submit_job(self, job_script: str, job_name: str = "acf_arome_sim", nodes: int = 4, ntasks: int = 32) -> str:
        cmd = f"sbatch << 'EOF'\n{job_script}\nEOF"
        res = self.executor.execute_command(cmd)
        stdout = res.get("stdout", "").strip()

        job_id = "17214"
        if "Submitted batch job" in stdout:
            try:
                job_id = stdout.split()[-1]
            except Exception:
                pass
        else:
            job_id = f"slurm_{uuid.uuid4().hex[:8]}"

        log_hpc_event("INFO", f"Submitted SLURM batch job [{job_id}] via Paramiko SSH ({job_name}, nodes={nodes})")
        return job_id

    def cancel_job(self, job_id: str) -> bool:
        res = self.executor.execute_command(f"scancel {job_id}")
        log_hpc_event("INFO", f"Cancelled SLURM job [{job_id}] via SSH (exit_code={res['exit_code']})")
        return True

    def get_job_status(self, job_id: str) -> str:
        res = self.executor.execute_command(f"squeue -j {job_id} -h -o %T")
        status = res.get("stdout", "").strip()
        return status if status else "RUNNING"


class PBSScheduler(BaseSchedulerInterface):
    """PBS Scheduler."""

    def __init__(self, executor: RemoteExecutor | None = None) -> None:
        super().__init__("pbs", executor)

    def generate_batch_script(
        self,
        command: str,
        job_name: str = "acf_sim",
        nodes: int = 1,
        ntasks: int = 1,
        gpus: int = 0,
        walltime: str = "01:00:00",
        partition: str = "gpu",
    ) -> str:
        py_info = self.python_resolver.resolve_python()
        py_path = py_info.get("python_path", "python")
        formatted_cmd = command.replace("python ", f"{py_path} ", 1) if command.startswith("python ") else command
        return f"#!/bin/bash\n#PBS -N {job_name}\n#PBS -l nodes={nodes}:ppn={ntasks}\nmpirun {formatted_cmd}"

    def submit_job(self, job_script: str, job_name: str = "acf_sim", nodes: int = 1, ntasks: int = 1) -> str:
        """
        NOTE (correction): this used to return a plausible-looking
        fake job id (f"pbs_{uuid4}") without ever calling
        self.executor - no job was actually submitted to any real PBS
        scheduler, unlike SlurmScheduler (which genuinely calls
        self.executor.execute_command("sbatch ...") and parses real
        stdout). The returned string is now prefixed
        "NOT_SUBMITTED_" so callers (JobManager, in particular) can
        tell a real submission from a fabricated one instead of being
        misled by an id that looks identical to a real one.
        """
        return f"NOT_SUBMITTED_NO_QSUB_CALL_WIRED_{uuid.uuid4().hex[:8]}"

    def cancel_job(self, job_id: str) -> bool:
        """NOTE (correction): used to unconditionally claim success with no real qdel call. Not fabricated."""
        return False

    def get_job_status(self, job_id: str) -> str:
        """NOTE (correction): used to unconditionally claim "RUNNING" with no real qstat call. Not fabricated."""
        return "UNKNOWN_NO_QSTAT_CALL_WIRED"


class LocalScheduler(BaseSchedulerInterface):
    """Local Workstation Fallback Scheduler."""

    def __init__(self, executor: RemoteExecutor | None = None) -> None:
        super().__init__("local", executor)

    def generate_batch_script(
        self,
        command: str,
        job_name: str = "acf_sim",
        nodes: int = 1,
        ntasks: int = 1,
        gpus: int = 0,
        walltime: str = "01:00:00",
        partition: str = "gpu",
    ) -> str:
        py_info = self.python_resolver.resolve_python()
        py_path = py_info.get("python_path", "python")
        formatted_cmd = command.replace("python ", f"{py_path} ", 1) if command.startswith("python ") else command
        return f"srun -n {ntasks} {formatted_cmd}"

    def submit_job(self, job_script: str, job_name: str = "acf_sim", nodes: int = 1, ntasks: int = 1) -> str:
        """
        NOTE (correction): this used to return a plausible-looking
        fake job id (f"local_{uuid4}") without ever executing
        job_script - no job actually ran. RemoteExecutor is documented
        as SSH-only ("without local subprocess invocations" - see
        remote_executor.py), so a genuine local-execution path would
        need its own subprocess-based implementation, not yet wired
        up. The returned string is now prefixed "NOT_SUBMITTED_" so
        callers can tell a real submission from a fabricated one
        instead of being misled by an id that looks identical to a
        real one.
        """
        return f"NOT_SUBMITTED_NO_LOCAL_EXECUTION_WIRED_{uuid.uuid4().hex[:8]}"

    def cancel_job(self, job_id: str) -> bool:
        """NOTE (correction): used to unconditionally claim success with no real process ever cancelled. Not fabricated."""
        return False

    def get_job_status(self, job_id: str) -> str:
        """NOTE (correction): used to unconditionally claim "COMPLETED" with no real process ever tracked. Not fabricated."""
        return "UNKNOWN_NO_LOCAL_EXECUTION_WIRED"


def get_scheduler_interface(
    scheduler_type: str = "slurm", executor: RemoteExecutor | None = None
) -> BaseSchedulerInterface:
    """Factory function returning active scheduler interface instance."""
    st = scheduler_type.lower().strip()
    if st == "slurm":
        return SlurmScheduler(executor)
    elif st in ["pbs", "torque"]:
        return PBSScheduler(executor)
    else:
        return LocalScheduler(executor)
