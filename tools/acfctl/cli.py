"""
Atmospheric Complexity Framework (ACF)

acfctl - Command-Line Interface

Real ``argparse``-based CLI: ``acfctl start|stop|status|report`` -
exactly the real command set
``docs/architecture/acf_reference_architecture.md`` names: "``acfctl``
was meant to become the operational control point: ``acfctl start |
stop | status | report ...``".
"""

from __future__ import annotations

import argparse
import sys

from tools.acfctl.apps import KNOWN_APPS
from tools.acfctl.processes import UnknownAppError
from tools.acfctl.processes import start as start_app
from tools.acfctl.processes import status as status_app
from tools.acfctl.processes import stop as stop_app
from tools.acfctl.report import build_health_report, format_health_report


def build_parser() -> argparse.ArgumentParser:
    """Real argument parser for the 4 real commands."""
    parser = argparse.ArgumentParser(prog="acfctl", description="ACF operational control point.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start", help="Start a real ACF app as a background process.")
    start_parser.add_argument("app", choices=sorted(KNOWN_APPS))

    stop_parser = subparsers.add_parser("stop", help="Stop a real, currently-running ACF app.")
    stop_parser.add_argument("app", choices=sorted(KNOWN_APPS))

    status_parser = subparsers.add_parser("status", help="Report whether a real ACF app is currently running.")
    status_parser.add_argument("app", choices=sorted(KNOWN_APPS))

    subparsers.add_parser("report", help="Real environment/health report for this ACF installation.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Real CLI entry point - returns a real process exit code (0 on
    success, 1 on a real, disclosed error), never raising out of
    ``main()`` itself so this is safe to use directly as a console-script
    target."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "start":
            pid = start_app(args.app)
            print(f"{args.app} started (pid {pid}).")
        elif args.command == "stop":
            stopped = stop_app(args.app)
            print(f"{args.app} stopped." if stopped else f"{args.app} was not running.")
        elif args.command == "status":
            current = status_app(args.app)
            state = f"running (pid {current.pid})" if current.running else "not running"
            print(f"{args.app}: {state}")
        elif args.command == "report":
            print(format_health_report(build_health_report()))
    except (UnknownAppError, FileNotFoundError, RuntimeError) as exc:
        print(f"acfctl: {exc}", file=sys.stderr)
        return 1
    return 0
