"""
Calibrate the AWCI convective (TCU/Cb) diagnosis against METAR, out of sample.

    .venv/bin/python tools/awci/calibrate_convection.py --data-dir DIR --domain north_africa \
        --train 2026092300,2026092312,2026092400,2026092412 --test 2026092500,2026092512,2026092600 \
        [--out report.json]

Cubes come from acf-awci-ingest, METAR from acf-awci-obs (same data directory). Pairs are built exactly as
in the verification (acf.awci.ops.verify); only pairs whose observed convection is known are used. The rule
is selected on the calibration runs only (acf.awci.ops.calibration_convection.select_rule) and reported on
each test run and on the pooled test runs, next to the current rule.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import timedelta
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from acf.awci.obs.store import ObsStore  # noqa: E402
from acf.awci.ops.calibration_convection import (  # noqa: E402
    ConvectiveSample, candidate_rules, evaluate, select_rule,
)
from acf.awci.ops.domains import DEFAULT_DOMAINS_PATH, load_domains  # noqa: E402
from acf.awci.ops.store import CubeStore  # noqa: E402
from acf.awci.ops.verify import VerifyConfig, build_pairs, model_at_stations  # noqa: E402

PREDICTORS = ("mucape", "column_condensate", "precip_rate")


def run_sample(root: Path, domain_name: str, run: str) -> ConvectiveSample:
    domain = load_domains(DEFAULT_DOMAINS_PATH)[domain_name]
    cubes, obs = CubeStore(root), ObsStore(root, domain_name)
    manifest = cubes.manifest(domain_name, run)
    stations = obs.stations()
    model = model_at_stations(cubes.dataset(domain_name, run), manifest, stations, domain, extra_fields=PREDICTORS)
    metars = obs.metars(model.valid_times[0] - timedelta(hours=1), model.valid_times[-1] + timedelta(hours=1))
    pairs, _ = build_pairs(model, stations, metars, VerifyConfig())
    known = [p for p in pairs if p.obs.convective is not None and p.model_convective is not None]
    return ConvectiveSample(
        observed=np.array([bool(p.obs.convective) for p in known], dtype=bool),
        base=np.array([bool(p.model_convective) for p in known], dtype=bool),
        predictors={name: np.array([model.extra[name][p.k, p.n] for p in known], dtype=float) for name in PREDICTORS},
    )


def pool(samples: list[ConvectiveSample]) -> ConvectiveSample:
    return ConvectiveSample(
        observed=np.concatenate([s.observed for s in samples]), base=np.concatenate([s.base for s in samples]),
        predictors={n: np.concatenate([s.predictors[n] for s in samples]) for n in PREDICTORS},
    )


def _row(label: str, s: dict[str, Any]) -> str:
    f = lambda v: "—" if v is None else f"{v:.2f}"  # noqa: E731
    return (f"| {label} | {s['n']} | {s['observed_events']} | {s['a']}/{s['b']}/{s['c']}/{s['d']} | "
            f"{f(s['pod'])} | {f(s['far'])} | {f(s['bias'])} | {f(s['ets'])} |")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--domain", default="north_africa")
    parser.add_argument("--train", required=True)
    parser.add_argument("--test", required=True)
    parser.add_argument("--bias-min", type=float, default=0.7)
    parser.add_argument("--bias-max", type=float, default=1.5)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    train_runs, test_runs = args.train.split(","), args.test.split(",")
    train = pool([run_sample(args.data_dir, args.domain, r) for r in train_runs])
    tests = {r: run_sample(args.data_dir, args.domain, r) for r in test_runs}
    best, table = select_rule(train, candidate_rules(), (args.bias_min, args.bias_max))
    top = sorted((t for t in table if t["ets"] is not None), key=lambda t: -t["ets"])[:10]
    report = {
        "domain": args.domain, "train_runs": train_runs, "test_runs": test_runs,
        "bias_range": [args.bias_min, args.bias_max], "selected_rule": best,
        "train": {"current": evaluate(train, {}), "selected": evaluate(train, best)},
        "test": {r: {"current": evaluate(s, {}), "selected": evaluate(s, best)} for r, s in tests.items()},
        "test_pooled": {"current": evaluate(pool(list(tests.values())), {}),
                        "selected": evaluate(pool(list(tests.values())), best)},
        "top10_train": top,
    }
    print(f"Selected rule (current AND): {best}\n")
    print("| Sample | n | Obs. | a/b/c/d | POD | FAR | Bias | ETS |\n|---|---|---|---|---|---|---|---|")
    print(_row("train, current", report["train"]["current"]))
    print(_row("train, selected", report["train"]["selected"]))
    for r in test_runs:
        print(_row(f"test {r}, current", report["test"][r]["current"]))
        print(_row(f"test {r}, selected", report["test"][r]["selected"]))
    print(_row("test pooled, current", report["test_pooled"]["current"]))
    print(_row("test pooled, selected", report["test_pooled"]["selected"]))
    if args.out:
        args.out.write_text(json.dumps(report, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
