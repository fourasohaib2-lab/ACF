#!/usr/bin/env python3
"""
Atmospheric Complexity Framework (ACF)

ACF Encyclopedia Adapter — Static-Analysis & Verification CLI (Étape 4, Phase 1)
==================================================================================

The original mission spec called for a full static-analysis/integration tool
(AST scanner, formula/unit validators, duplicate/conflict detectors, NWP model
adapters, 3-mode CLI) — a substantial, multi-week project on its own. This is
Phase 1: it formalizes the two ad-hoc verification techniques that this
session's manual encyclopedia audit actually proved high-value, as permanent,
reusable, CI-checkable tools, rather than one-off scratchpad scripts:

  scan     Confirms EncyclopediaRegistry initializes without a key collision
           (now structurally prevented by a hard guard in register() - see
           the "5 real collisions" fix this session, one of which silently
           discarded a working compute_func for 100+ commits before it was
           found), and flags *soft* duplicates: distinct keys registering
           near-identical equation text, which the hard guard does not (and
           should not) catch, but which are worth a human's attention.

  verify   Runs every entry's compute_func with 2 distinct, per-parameter-
           jittered probe-value sets and flags: exceptions, non-finite
           results, and "same output regardless of input" - the technique
           that found the doppler_velocity_dealiasing and
           vector_calculus_spherical formula-mismatch bugs this session.
           A flagged entry is NOT automatically wrong - array-typed and
           boolean-typed parameters routinely need per-entry review (see
           the manual literature-verification work this session) - this
           tool narrows the search space, it does not replace judgment.

  report   Runs both and prints one combined summary with a CI-friendly
           exit code (non-zero if any collision, hard error, or non-finite
           result is found; soft duplicates and insensitivity flags are
           reported but do not fail the exit code, since some are
           deliberately-simplified building blocks rather than bugs).

Explicitly NOT attempted in this phase (left for a future pass, per the
mission's own acknowledgment that its full scope is unrealistic in one
session): formula/unit dimensional validation, NWP model adapters, coefficient
literature-provenance checking (this session did that manually via WebSearch
for ~30 entries - automating literature verification itself is not
practical), and AST-based static analysis of the *implementation* source
(distinct from the runtime-probing "verify" mode here).

Usage:
    python tools/acf_encyclopedia_adapter.py scan
    python tools/acf_encyclopedia_adapter.py verify
    python tools/acf_encyclopedia_adapter.py report
    python tools/acf_encyclopedia_adapter.py report --json
"""

from __future__ import annotations

import argparse
import inspect
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from acf.science.encyclopedia.registry import EncyclopediaRegistry  # noqa: E402

# ---------------------------------------------------------------------------
# Data model for findings
# ---------------------------------------------------------------------------


@dataclass
class ScanResult:
    total_entries: int = 0
    collision_error: str | None = None
    soft_duplicates: list[tuple[str, str, str]] = field(default_factory=list)  # (key1, key2, normalized_equation)


@dataclass
class VerifyFinding:
    key: str
    reason: str  # "exception" | "non_finite" | "insensitive" | "skipped_array_input"
    detail: str


@dataclass
class VerifyResult:
    total_computable: int = 0
    checked: int = 0
    findings: list[VerifyFinding] = field(default_factory=list)


# ---------------------------------------------------------------------------
# scan mode
# ---------------------------------------------------------------------------


def _normalize_equation(eq: str) -> str:
    """Collapse whitespace and lowercase, for soft-duplicate comparison."""
    return re.sub(r"\s+", " ", eq.strip().lower())


def run_scan() -> ScanResult:
    """
    Confirms the registry initializes without a hard key collision (the
    EncyclopediaRegistry.register() guard would raise ValueError if one
    existed - this call surfaces that clearly, with a CI-friendly message,
    instead of it only being discovered incidentally by whichever test
    happens to import the encyclopedia first), then scans for *soft*
    duplicates: distinct keys with near-identical normalized equation text,
    which the hard guard intentionally does not flag (two entries CAN
    legitimately present the same physical law from two different domains
    - e.g. this session's boussinesq_approximation_momentum_form vs.
    dynamics.py's boussinesq_approximation - that's not an error, just
    worth a human glance).
    """
    result = ScanResult()
    try:
        EncyclopediaRegistry._ensure_initialized()
    except ValueError as exc:
        result.collision_error = str(exc)
        return result

    entries = EncyclopediaRegistry._entries
    result.total_entries = len(entries)

    by_equation: dict[str, list[str]] = {}
    for entry in entries.values():
        if not entry.equation:
            continue
        norm = _normalize_equation(entry.equation)
        by_equation.setdefault(norm, []).append(entry.key)

    for norm, keys in by_equation.items():
        if len(keys) < 2:
            continue
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                result.soft_duplicates.append((keys[i], keys[j], norm))

    return result


# ---------------------------------------------------------------------------
# verify mode
# ---------------------------------------------------------------------------

# Two distinct probe-value sets. Each is a function of (param_name, position)
# so that different parameters within one call get different jittered values
# rather than all sharing an identical fallback (the bug that caused false
# "constant regardless of input" positives in the earlier, less careful
# version of this technique - documented in this session's progress notes).
_PROBE_BASE_SETS: tuple[dict[str, float], ...] = (
    {"scale": 1.0, "offset": 0.0},
    {"scale": 2.3, "offset": 1.0},
)


def _jittered_value(param_name: str, position: int, probe_set: dict[str, float]) -> float:
    # Deterministic pseudo-random jitter keyed by (name, position, probe set),
    # so re-runs are reproducible but different parameters/probe-sets diverge.
    seed = sum(ord(c) for c in param_name) + position * 17
    base = 1.0 + (seed % 11) * 0.37
    return base * probe_set["scale"] + probe_set["offset"]


_BOOL_LIKE_NAMES = {"is_marine", "is_kelvin", "wet_growth"}


def _build_probe_kwargs(func: Any, probe_set: dict[str, float]) -> dict[str, Any] | None:
    """Builds a kwargs dict for one probe call, or None if the signature can't be probed safely."""
    try:
        sig = inspect.signature(func)
    except (TypeError, ValueError):
        return None

    kwargs: dict[str, Any] = {}
    for position, (name, param) in enumerate(sig.parameters.items()):
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        annotation = str(param.annotation)
        if "list" in annotation or "ndarray" in annotation or "tuple" in annotation:
            return None  # array-typed input: needs a dedicated, per-entry probe - skip, don't fake it
        if name in _BOOL_LIKE_NAMES:
            kwargs[name] = probe_set["scale"] > 1.5  # deterministic but differs between the two probe sets
        elif annotation == "<class 'int'>" or annotation == "int":
            # Coerce int-annotated parameters (e.g. an iteration count fed to
            # range()) instead of passing a raw jittered float, which would
            # raise a spurious TypeError unrelated to the entry's own physics.
            kwargs[name] = int(round(_jittered_value(name, position, probe_set)))
        else:
            kwargs[name] = _jittered_value(name, position, probe_set)
    return kwargs


def run_verify() -> VerifyResult:
    EncyclopediaRegistry._ensure_initialized()
    entries = EncyclopediaRegistry._entries
    computable = {k: v for k, v in entries.items() if v.compute_func is not None}

    result = VerifyResult(total_computable=len(computable))

    for key, entry in sorted(computable.items()):
        func = entry.compute_func
        if func is None:
            continue  # unreachable given the `computable` filter above; narrows the type for mypy
        kwargs_a = _build_probe_kwargs(func, _PROBE_BASE_SETS[0])
        kwargs_b = _build_probe_kwargs(func, _PROBE_BASE_SETS[1])
        if kwargs_a is None or kwargs_b is None:
            result.findings.append(
                VerifyFinding(key, "skipped_array_input", "compute_func takes an array/list/tuple argument")
            )
            continue

        result.checked += 1
        try:
            out_a = func(**kwargs_a)
            out_b = func(**kwargs_b)
        except NotImplementedError as exc:
            # An honest, deliberate disclosure (e.g. lfc_height_equation,
            # el_height_equation - fabricated formulas removed earlier this
            # session in favor of raising) - not a crash to flag as a bug.
            result.findings.append(VerifyFinding(key, "honestly_unimplemented", str(exc)[:120]))
            continue
        except Exception as exc:  # noqa: BLE001 - deliberately broad: any other crash is a real finding
            result.findings.append(VerifyFinding(key, "exception", f"{type(exc).__name__}: {exc}"))
            continue

        for label, out in (("A", out_a), ("B", out_b)):
            if isinstance(out, int | float) and not math.isfinite(out):
                result.findings.append(VerifyFinding(key, "non_finite", f"probe {label} -> {out!r}"))

        if isinstance(out_a, int | float) and isinstance(out_b, int | float):
            if math.isclose(out_a, out_b, rel_tol=1e-9, abs_tol=1e-12):
                result.findings.append(
                    VerifyFinding(key, "insensitive", f"identical output for two distinct probe sets: {out_a!r}")
                )

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _print_scan(result: ScanResult) -> int:
    if result.collision_error:
        print("SCAN: FAILED - registry key collision detected")
        print(f"  {result.collision_error}")
        return 1

    print(f"SCAN: {result.total_entries} entries registered, 0 key collisions (guarded at source)")
    if result.soft_duplicates:
        print(f"  {len(result.soft_duplicates)} soft duplicate(s) - same equation text under different keys:")
        for key1, key2, _norm in result.soft_duplicates:
            print(f"    '{key1}' <-> '{key2}'")
        print("  (not an error - review manually; may be a deliberate cross-domain restatement)")
    return 0


def _print_verify(result: VerifyResult) -> int:
    hard_findings = [f for f in result.findings if f.reason in ("exception", "non_finite")]
    soft_findings = [f for f in result.findings if f.reason not in ("exception", "non_finite")]

    print(f"VERIFY: {result.checked}/{result.total_computable} compute_func entries probed")
    if hard_findings:
        print(f"  {len(hard_findings)} HARD finding(s) (crash / non-finite output):")
        for f in hard_findings:
            print(f"    [{f.reason}] '{f.key}': {f.detail}")
    if soft_findings:
        print(f"  {len(soft_findings)} soft finding(s) (needs manual review, not necessarily a bug):")
        for f in soft_findings:
            print(f"    [{f.reason}] '{f.key}': {f.detail}")
    if not result.findings:
        print("  no findings")
    return 1 if hard_findings else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="acf_encyclopedia_adapter",
        description="Static-analysis & verification CLI for science/encyclopedia/ (Étape 4, Phase 1).",
    )
    parser.add_argument("mode", choices=["scan", "verify", "report"], help="Which check(s) to run.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of text.")
    args = parser.parse_args(argv)

    scan_result = run_scan() if args.mode in ("scan", "report") else None
    verify_result = run_verify() if args.mode in ("verify", "report") else None

    if args.json:
        payload: dict[str, Any] = {}
        if scan_result is not None:
            payload["scan"] = {
                "total_entries": scan_result.total_entries,
                "collision_error": scan_result.collision_error,
                "soft_duplicates": scan_result.soft_duplicates,
            }
        if verify_result is not None:
            payload["verify"] = {
                "total_computable": verify_result.total_computable,
                "checked": verify_result.checked,
                "findings": [
                    {"key": f.key, "reason": f.reason, "detail": f.detail} for f in verify_result.findings
                ],
            }
        print(json.dumps(payload, indent=2))
    else:
        exit_code = 0
        if scan_result is not None:
            exit_code = max(exit_code, _print_scan(scan_result))
        if verify_result is not None:
            exit_code = max(exit_code, _print_verify(verify_result))
        return exit_code

    # JSON mode: compute exit code without re-printing.
    exit_code = 0
    if scan_result is not None and scan_result.collision_error:
        exit_code = 1
    if verify_result is not None and any(f.reason in ("exception", "non_finite") for f in verify_result.findings):
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
