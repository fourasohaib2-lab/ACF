"""
Probabilistic verification of AWCI IFS ENS products against METAR, pooled over several runs (spec SP5b).

    .venv/bin/python tools/awci/verify_ensemble.py --data-dir DIR --domain north_africa \
        --runs 2026092412,2026092500,2026092512,2026092600 [--out report.json]

Each run needs its deterministic cube (acf-awci-ingest) and its ENS cube (acf-awci-ens) in the data directory,
and the METAR archive (acf-awci-obs). Scores and definitions: acf.awci.ops.verify_ens.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from acf.awci.ops.domains import DEFAULT_DOMAINS_PATH, load_domains  # noqa: E402
from acf.awci.ops.verify import VerifyConfig  # noqa: E402
from acf.awci.ops.verify_ens import ENS_EVENTS, run_samples, verify_ens_run  # noqa: E402


def _f(v: float | None, digits: int = 3) -> str:
    return "—" if v is None else f"{v:.{digits}f}"


def _row(label: str, s: dict[str, Any]) -> str:
    return (f"| {label} | {s['n']} | {s['observed_events']} | {_f(s.get('observed_frequency'))} | "
            f"{_f(s.get('mean_probability'))} | {_f(s['brier'])} | {_f(s['fair_brier'])} | "
            f"{_f(s['brier_deterministic'])} | {_f(s['bss_climatology'], 2)} | {_f(s['skill_vs_deterministic'], 2)} |")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--domain", default="north_africa")
    parser.add_argument("--runs", required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    domain = load_domains(DEFAULT_DOMAINS_PATH)[args.domain]
    config = VerifyConfig()
    runs = args.runs.split(",")
    per_run, pooled, exclusions, profiles = {}, [], Counter(), {}
    for run in runs:
        samples, excl, prof = run_samples(args.data_dir, domain, run, config)
        per_run[run] = verify_ens_run(samples, excl, config, prof)
        pooled += samples
        exclusions.update(excl)
        profiles[run] = prof
    same = len({(p["ens"], p["deterministic"]) for p in profiles.values()}) == 1
    first = next(iter(profiles.values()))
    report = {"domain": args.domain, "runs": runs, "per_run": per_run, "cloud_profiles": profiles,
              "pooled": verify_ens_run(pooled, dict(exclusions), config, first if same else {"ens": None,
                                                                                         "deterministic": "mixed"})}
    header = ("| Échantillon | n | Obs. | Fréq. obs. | P moyenne | BS ENS | BS fair | BS dét. | BSS clim. | "
              "Gain / dét. |\n|---|---|---|---|---|---|---|---|---|---|")
    for event in ENS_EVENTS:
        print(f"\n### {event}\n\n{header}")
        for run in runs:
            print(_row(run, per_run[run]["events"][event]["total"]))
        print(_row("cumul", report["pooled"]["events"][event]["total"]))
        print("\n| Classe de P | n | P moyenne | Fréq. obs. |\n|---|---|---|---|")
        for b in report["pooled"]["events"][event]["total"]["diagram"]:
            if b["n"]:
                print(f"| {b['lower']:.1f}–{b['upper']:.1f} | {b['n']} | {_f(b['mean_forecast'])} | "
                      f"{_f(b['observed_frequency'])} |")
    print(f"\nProfils nuageux (ENS / déterministe) : {profiles}")
    print(f"Exclusions cumulées : {dict(exclusions)}")
    if args.out:
        args.out.write_text(json.dumps(report, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
