"""
Score IFS and GFS against METAR on the same runs (spec SP6 §1.3): contingency scores of the SP3 verification
(acf.awci.ops.verify) pooled over the runs, per model, on each model's own pairs (same stations, same valid times,
same METAR matching; only cells with a model value count).

    .venv/bin/python tools/awci/compare_models_verification.py --data-dir DIR --domain north_africa \
        --runs 2026092412,2026092500,2026092512,2026092600 [--out report.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import timedelta
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from acf.awci.obs.store import ObsStore  # noqa: E402
from acf.awci.ops.domains import DEFAULT_DOMAINS_PATH, load_domains  # noqa: E402
from acf.awci.ops.store import CubeStore, model_root  # noqa: E402
from acf.awci.ops.verify import Pair, VerifyConfig, build_pairs, model_at_stations, verify_run  # noqa: E402


def pairs_of(root: Path, model: str, domain_name: str, run: str) -> tuple[list[Pair], dict[str, int], str]:
    domain = load_domains(DEFAULT_DOMAINS_PATH)[domain_name]
    cubes, obs = CubeStore(model_root(root, model)), ObsStore(root, domain_name)
    manifest = cubes.manifest(domain_name, run)
    stations = obs.stations()
    at = model_at_stations(cubes.dataset(domain_name, run), manifest, stations, domain)
    metars = obs.metars(at.valid_times[0] - timedelta(hours=1), at.valid_times[-1] + timedelta(hours=1))
    pairs, excluded = build_pairs(at, stations, metars, VerifyConfig())
    return pairs, excluded, str(manifest.get("cloud_profile_version"))


def _f(v: float | None) -> str:
    return "—" if v is None else f"{v:.2f}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--domain", default="north_africa")
    parser.add_argument("--runs", required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    runs = args.runs.split(",")
    report: dict[str, Any] = {"runs": runs, "domain": args.domain, "models": {}}
    for model in ("ifs", "gfs"):
        pairs: list[Pair] = []
        excluded: dict[str, int] = {}
        profiles = set()
        for run in runs:
            p, e, prof = pairs_of(args.data_dir, model, args.domain, run)
            pairs += p
            profiles.add(prof)
            for k, v in e.items():
                excluded[k] = excluded.get(k, 0) + v
        report["models"][model] = verify_run(pairs, excluded, VerifyConfig(), stations_total=0) | {
            "cloud_profiles": sorted(profiles)}
    print("| Événement | Modèle | n | Obs. | a/b/c/d | POD | FAR | Biais | ETS |\n|---|---|---|---|---|---|---|---|---|")
    for event in report["models"]["ifs"]["events"]:
        for model in ("ifs", "gfs"):
            t = report["models"][model]["events"][event]["total"]
            print(f"| {event} | {model.upper()} | {t['n']} | {t['observed_events']} | {t['a']}/{t['b']}/{t['c']}/{t['d']} | "
                  f"{_f(t['pod'])} | {_f(t['far'])} | {_f(t['bias'])} | {_f(t['ets'])} |")
    for model in ("ifs", "gfs"):
        err = report["models"][model]["ceiling_base_error_ft"]
        print(f"{model.upper()} base du plafond : n={err['n']} biais={_f(err['mean_error'])} ft MAE={_f(err['mae'])} ft ; "
              f"profils nuageux {report['models'][model]['cloud_profiles']}")
    if args.out:
        args.out.write_text(json.dumps(report, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
