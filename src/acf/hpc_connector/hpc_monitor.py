"""
Atmospheric Complexity Framework (ACF)

HPC CONNECTOR - Slurm Cluster Monitoring Engine (ACF-HPC-003)

Provides cluster monitoring routines wrapping Slurm utilities (squeue, sacct, sinfo, scontrol, sdiag).

NOTE (correction): every method below used to fall back to hard-coded,
realistic-looking fake cluster/job data (e.g. jobs "acf_arome_00z"/
"acf_aladin_00z" in RUNNING/PENDING state, "142 jobs submitted, 138
completed, 2 failed") with zero disclosure whenever the real squeue/
sacct/sinfo/scontrol/sdiag binaries were unavailable - which is the
case in essentially any environment outside a real, configured Slurm
cluster (verified: every existing test mocks real command output via
MockRemoteExecutor; only test_error_resilience exercises this fallback
path, and only asserts loose structural properties, not the specific
fabricated values). A caller with no real scheduler backend had no way
to distinguish this fake data from a genuine cluster snapshot. Each
method now returns an explicit `"connected": bool` field so callers
can always tell real from fake, and no longer fabricates plausible-
looking numbers for the case where nothing is actually connected.
"""

from __future__ import annotations

import re
import shlex
import shutil
import subprocess
from typing import Any


class HPCMonitor:
    """
    Slurm Cluster Monitoring class for ACF HPC execution platform.
    """

    def __init__(self, remote_executor: Any | None = None, cluster_name: str = "Fennec") -> None:
        """
        Initialize HPCMonitor with an optional remote_executor or local subprocess.
        """
        self.remote_executor = remote_executor
        self.cluster_name = cluster_name

    def _exec_command(self, cmd: str) -> str:
        """
        Execute a shell command either via remote_executor or local subprocess.
        """
        if self.remote_executor and hasattr(self.remote_executor, "execute_command"):
            try:
                res = self.remote_executor.execute_command(cmd)
                if isinstance(res, dict):
                    return res.get("output", "") or res.get("stdout", "")
                return str(res)
            except Exception:
                pass

        bin_name = cmd.split()[0]
        if not shutil.which(bin_name):
            return ""

        try:
            res = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
            return res.stdout.strip()
        except Exception:
            return ""

    def list_jobs(self, user: str | None = None) -> list[dict[str, Any]]:
        """
        List active and queued Slurm jobs via squeue.

        NOTE (hardening): `user` used to be interpolated directly into a
        shell command string executed via subprocess.run(shell=True) (or
        sent as-is to a remote SSH executor) - a shell-metacharacter-
        containing value (e.g. a stray `;`, `` ` ``, or `$()`) could
        inject arbitrary commands. No caller currently passes anything
        but a trusted local value (verified via grep), but this is cheap
        to close properly rather than rely on that holding forever -
        shlex.quote() makes the value safe to embed in a POSIX shell
        command line either locally or over SSH.
        """
        user_flag = f"-u {shlex.quote(user)}" if user else ""
        cmd = f'squeue {user_flag} --format="%i|%j|%u|%T|%M|%D|%R" -h'
        output = self._exec_command(cmd)

        jobs: list[dict[str, Any]] = []
        if output:
            for line in output.strip().splitlines():
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 7:
                    try:
                        n_nodes = int(parts[5])
                    except ValueError:
                        n_nodes = 1

                    jobs.append(
                        {
                            "job_id": parts[0],
                            "job_name": parts[1],
                            "user": parts[2],
                            "state": parts[3],
                            "elapsed_time": parts[4],
                            "nodes": n_nodes,
                            "node_list": parts[6],
                            "connected": True,
                        }
                    )
            return jobs

        # NOTE (correction): used to fabricate 2 fake jobs (1001/1002,
        # "acf_arome_00z"/"acf_aladin_00z") when squeue is unavailable.
        # No real scheduler connected - honestly empty rather than invented.
        return []

    def get_job_history(self, job_id: str) -> dict[str, Any]:
        """
        Get finished job history and accounting details via sacct.

        NOTE (hardening): `job_id` used to be interpolated directly into
        the shell command string - see list_jobs()'s NOTE (hardening)
        for the same reasoning. shlex.quote()'d before use.
        """
        cmd = f"sacct -j {shlex.quote(job_id)} --format=JobID,State,Elapsed,NNodes,NodeList,ExitCode -P -n"
        output = self._exec_command(cmd)

        if output:
            lines = output.strip().splitlines()
            if lines:
                parts = [p.strip() for p in lines[0].split("|")]
                if len(parts) >= 6:
                    try:
                        n_nodes = int(parts[3])
                    except ValueError:
                        n_nodes = 1

                    return {
                        "job_id": parts[0],
                        "state": parts[1],
                        "elapsed_time": parts[2],
                        "nodes": n_nodes,
                        "node_list": parts[4],
                        "exit_code": parts[5],
                        "connected": True,
                    }

        # NOTE (correction): used to fabricate a fake "COMPLETED" job
        # history (00:45:12 elapsed, exit code 0:0) for ANY job_id when
        # sacct is unavailable. No real accounting backend connected.
        return {
            "job_id": str(job_id),
            "state": "NOT_AVAILABLE_NO_SCHEDULER_BACKEND_CONNECTED",
            "elapsed_time": None,
            "nodes": None,
            "node_list": None,
            "exit_code": None,
            "connected": False,
        }

    def cluster_status(self) -> dict[str, Any]:
        """
        Get cluster summary status via sinfo.
        """
        cmd = 'sinfo -o "%P|%a|%F" -h'
        output = self._exec_command(cmd)

        idle_nodes = 0
        allocated_nodes = 0
        down_nodes = 0
        partitions: list[dict[str, Any]] = []

        if output:
            for line in output.strip().splitlines():
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 3:
                    part_name = parts[0].rstrip("*")
                    avail = parts[1]
                    nodes_counts = parts[2].split("/")
                    if len(nodes_counts) == 4:
                        try:
                            a = int(nodes_counts[0])
                            i = int(nodes_counts[1])
                            o = int(nodes_counts[2])
                            allocated_nodes += a
                            idle_nodes += i
                            down_nodes += o
                        except ValueError:
                            pass

                    partitions.append(
                        {
                            "partition": part_name,
                            "available": avail,
                            "nodes_summary": parts[2],
                        }
                    )

            return {
                "idle_nodes": idle_nodes,
                "allocated_nodes": allocated_nodes,
                "down_nodes": down_nodes,
                "partitions": partitions,
                "connected": True,
            }

        # NOTE (correction): used to fabricate a fake 32-node cluster
        # (12 idle, 20 allocated, 2 partitions "hpc_normal"/"hpc_gpu")
        # when sinfo is unavailable. No real scheduler connected.
        return {
            "idle_nodes": 0,
            "allocated_nodes": 0,
            "down_nodes": 0,
            "partitions": [],
            "connected": False,
        }

    def node_status(self, node_name: str | None = None) -> dict[str, Any] | list[dict[str, Any]]:
        """
        Get detailed node metrics via scontrol show node.

        NOTE (hardening): `node_name` used to be interpolated directly
        into the shell command string - see list_jobs()'s NOTE
        (hardening) for the same reasoning. shlex.quote()'d before use.
        """
        target = shlex.quote(node_name) if node_name else ""
        cmd = f"scontrol show node {target}"
        output = self._exec_command(cmd)

        nodes: list[dict[str, Any]] = []
        if output:
            raw_nodes = output.strip().split("\n\n")
            for block in raw_nodes:
                if not block.strip():
                    continue

                name_match = re.search(r"NodeName=(\S+)", block)
                cpu_tot_match = re.search(r"CPUTot=(\d+)", block)
                cpu_alloc_match = re.search(r"CPUAlloc=(\d+)", block)
                mem_match = re.search(r"RealMemory=(\d+)", block)
                state_match = re.search(r"State=(\S+)", block)

                name = name_match.group(1) if name_match else "unknown"
                cpu_tot = int(cpu_tot_match.group(1)) if cpu_tot_match else 64
                cpu_alloc = int(cpu_alloc_match.group(1)) if cpu_alloc_match else 0
                mem_mb = int(mem_match.group(1)) if mem_match else 256000
                st = state_match.group(1) if state_match else "IDLE"

                nodes.append(
                    {
                        "node_name": name,
                        "cpus_total": cpu_tot,
                        "cpus_alloc": cpu_alloc,
                        "cpus_avail": max(0, cpu_tot - cpu_alloc),
                        "memory_mb": mem_mb,
                        "state": st,
                        "connected": True,
                    }
                )

            if node_name and nodes:
                return nodes[0]
            return nodes

        # NOTE (correction): used to fabricate 2 fake nodes ("node01"
        # ALLOCATED 32/64 CPUs, "node02" IDLE) when scontrol is
        # unavailable. No real scheduler connected - honestly empty
        # rather than invented.
        if node_name:
            return {
                "node_name": node_name,
                "cpus_total": None,
                "cpus_alloc": None,
                "cpus_avail": None,
                "memory_mb": None,
                "state": "NOT_AVAILABLE_NO_SCHEDULER_BACKEND_CONNECTED",
                "connected": False,
            }
        return []

    def get_cluster_health(self) -> dict[str, Any]:
        """
        Calculates and returns overall cluster health summary.

        Expected return structure:
        {
            "cluster": "Fennec",
            "scheduler": "slurm",
            "nodes_total": 32,
            "nodes_idle": 12,
            "nodes_down": 0,
            "jobs_running": 1,
            "jobs_pending": 1,
            "cpu_load": 62.5,
            "memory_available": 75.0
        }
        """
        c_status = self.cluster_status()
        jobs = self.list_jobs()

        # NOTE (correction): `total_nodes` used to fall back to a
        # fabricated 32 whenever idle+alloc+down summed to 0 - including
        # the genuinely disconnected case (0/0/0), silently claiming a
        # 32-node cluster exists when nothing was actually queried.
        idle = c_status.get("idle_nodes", 0)
        alloc = c_status.get("allocated_nodes", 0)
        down = c_status.get("down_nodes", 0)
        total_nodes = idle + alloc + down

        running_jobs = sum(1 for j in jobs if j.get("state") == "RUNNING")
        pending_jobs = sum(1 for j in jobs if j.get("state") == "PENDING")

        cpu_info = self.get_cpu_usage()
        mem_info = self.get_memory_usage()

        return {
            "cluster": self.cluster_name,
            "scheduler": "slurm",
            "nodes_total": total_nodes,
            "nodes_idle": idle,
            "nodes_down": down,
            "jobs_running": running_jobs,
            "jobs_pending": pending_jobs,
            "cpu_load": cpu_info.get("cpu_load_pct"),
            "memory_available": mem_info.get("memory_available_pct"),
            "connected": bool(c_status.get("connected")),
        }

    def get_partition_status(self) -> list[dict[str, Any]]:
        """
        Returns status of all available Slurm partitions.
        """
        c_status = self.cluster_status()
        return c_status.get("partitions", [])

    def get_node_health(self) -> list[dict[str, Any]]:
        """
        Returns health status and utilization for all compute nodes.
        """
        nodes = self.node_status()
        if isinstance(nodes, dict):
            nodes = [nodes]

        node_health_list: list[dict[str, Any]] = []
        for n in nodes:
            name = n.get("node_name", "unknown")
            st = n.get("state", "UNKNOWN")
            is_healthy = st.upper() not in ["DOWN", "DRAIN", "FAIL"]
            node_health_list.append(
                {
                    "node_name": name,
                    "healthy": is_healthy,
                    "state": st,
                    "cpus_total": n.get("cpus_total", 64),
                    "cpus_alloc": n.get("cpus_alloc", 0),
                    "memory_mb": n.get("memory_mb", 256000),
                }
            )
        return node_health_list

    def get_cpu_usage(self) -> dict[str, Any]:
        """
        Returns overall cluster CPU load and availability statistics.

        NOTE (correction): `cpu_load_pct` used to fall back to a
        fabricated 50.0% whenever total_cpus was 0 - including the
        genuinely disconnected case (node_status() returning no nodes),
        silently claiming a plausible-looking mid-range load with no
        real nodes queried at all.
        """
        nodes = self.node_status()
        if isinstance(nodes, dict):
            nodes = [nodes]

        total_cpus = sum(n.get("cpus_total") or 0 for n in nodes)
        alloc_cpus = sum(n.get("cpus_alloc") or 0 for n in nodes)
        avail_cpus = max(0, total_cpus - alloc_cpus)
        pct = (alloc_cpus / total_cpus * 100.0) if total_cpus > 0 else None

        return {
            "cpus_total": total_cpus,
            "cpus_allocated": alloc_cpus,
            "cpus_available": avail_cpus,
            "cpu_load_pct": round(pct, 2) if pct is not None else None,
            "connected": bool(nodes),
        }

    def get_memory_usage(self) -> dict[str, Any]:
        """
        Returns overall cluster memory usage statistics.

        NOTE (correction): `memory_available_pct`/the underlying
        allocation ratio used to fall back to fabricated 75.0%/0.25
        defaults whenever there was no real node data at all
        (total_mem_mb == 0 or total_cpus == 0), silently claiming
        plausible-looking utilization for a cluster that was never
        actually queried.
        """
        nodes = self.node_status()
        if isinstance(nodes, dict):
            nodes = [nodes]

        total_mem_mb = sum(n.get("memory_mb") or 0 for n in nodes)
        # Approximate memory utilization based on allocated CPUs
        total_cpus = sum(n.get("cpus_total") or 0 for n in nodes)
        alloc_cpus = sum(n.get("cpus_alloc") or 0 for n in nodes)
        ratio = (alloc_cpus / total_cpus) if total_cpus > 0 else None

        if ratio is None or total_mem_mb == 0:
            return {
                "memory_total_mb": total_mem_mb,
                "memory_used_mb": None,
                "memory_available_mb": None,
                "memory_available_pct": None,
                "connected": bool(nodes),
            }

        used_mem_mb = int(total_mem_mb * ratio)
        avail_mem_mb = max(0, total_mem_mb - used_mem_mb)
        pct_avail = avail_mem_mb / total_mem_mb * 100.0

        return {
            "memory_total_mb": total_mem_mb,
            "memory_used_mb": used_mem_mb,
            "memory_available_mb": avail_mem_mb,
            "memory_available_pct": round(pct_avail, 2),
            "connected": True,
        }

    def get_slurm_statistics(self) -> dict[str, Any]:
        """
        Extracts Slurm daemon statistics via sdiag.
        """
        output = self._exec_command("sdiag")
        if output:
            stats: dict[str, Any] = {}
            for line in output.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    stats[k.strip()] = v.strip()
            stats["connected"] = True
            return stats

        # NOTE (correction): used to fabricate fake Slurm daemon
        # statistics ("142 jobs submitted, 138 completed, 2 failed")
        # when sdiag is unavailable. No real scheduler daemon connected.
        return {
            "server_thread_count": None,
            "agent_queue_size": None,
            "jobs_submitted": None,
            "jobs_started": None,
            "jobs_completed": None,
            "jobs_failed": None,
            "connected": False,
        }
