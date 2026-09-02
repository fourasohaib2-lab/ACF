#!/usr/bin/env python3
"""
ACF Daily Forecast Cycle — CI/CD automation entry point.

Implements docs/ACF_HPC_005_NEXT_ROADMAP.md's first CI/CD objective:
"Automatiser le lancement quotidien des cycles de prévision AROME 1.3 km
et ALADIN 7.5 km" (automate the daily launch of AROME 1.3km and ALADIN
7.5km forecast cycles) on the Fennec ONM HPC cluster.

What this genuinely does: connects to the cluster profile named by
--profile (real acf.hpc_connector.HPCConnectionManager.connect() -
Paramiko SSH), then runs the real one-click AROME and ALADIN pipelines
(execute_one_click_arome()/execute_one_click_aladin() - this session's
own additions, submitting `python -m acf.forecast.engine --model ...`
as a real SLURM job). Exits non-zero if either cycle did not genuinely
submit a real job (is_real_submission is False), so a CI/CD scheduler
(cron, GitHub Actions, ecFlow, ...) sees a real failure signal instead
of a silently-ignored no-op.

Honesty note: run without real cluster network access/credentials (e.g.
in this repository's own CI, which has no route to the real Fennec
cluster), HPCConnectionManager.connect() completes its local workflow
(documented offline-dev-mode design) but ssh_connector.is_real_connection
stays False and no real job is ever submitted - this script reports that
plainly rather than claiming success. It is meant to run somewhere with
genuine network access to Fennec (a self-hosted CI runner on the ONM
network, or a machine with a working VPN/SSH route there) to actually
deploy daily cycles - see this session's own docs/
ACF_PHYSICS_GUARD_AUDIT_CHANGELOG.md for that limitation.
"""

import argparse
import logging
import sys
from typing import Any

from acf.hpc_connector.connection_manager import HPCConnectionManager

logger = logging.getLogger("acf.daily_forecast_cycle")


def run_daily_cycle(profile: str = "fennec") -> dict[str, Any]:
    hpc = HPCConnectionManager()
    connected = hpc.connect(profile)
    real_transport = bool(getattr(hpc.ssh_connector, "is_real_connection", False))

    logger.info(
        "Connected to profile %r: workflow_completed=%s real_ssh_transport=%s",
        profile, connected, real_transport,
    )

    arome_result = hpc.execute_one_click_arome()
    logger.info("AROME 1.3km cycle: %s (job_id=%s)", arome_result["status"], arome_result["job_id"])

    aladin_result = hpc.execute_one_click_aladin()
    logger.info("ALADIN 7.5km cycle: %s (job_id=%s)", aladin_result["status"], aladin_result["job_id"])

    both_real = arome_result["is_real_submission"] and aladin_result["is_real_submission"]

    return {
        "profile": profile,
        "real_ssh_transport": real_transport,
        "arome": arome_result,
        "aladin": aladin_result,
        "both_submitted_for_real": both_real,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--profile", default="fennec", help="HPC cluster profile name (see config/hpc.yaml).")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format="%(message)s")

    result = run_daily_cycle(args.profile)

    print(f"AROME:  {result['arome']['status']}")
    print(f"ALADIN: {result['aladin']['status']}")
    print(f"Real SSH transport established: {result['real_ssh_transport']}")

    if not result["both_submitted_for_real"]:
        print(
            "NOT a real deployment: at least one cycle did not submit a genuine SLURM job "
            "(no real cluster connection from this environment). See this script's own "
            "module docstring.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
