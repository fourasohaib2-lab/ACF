"""
Score IFS and GFS columns against radiosondes over several runs (spec SP7 §5): acf.awci.ops.verify_sounding pooled
over the runs, per model, in total and per lead time (a sounding pairs with every run that has a step at its nominal
time, once per run).

    .venv/bin/python tools/awci/verify_soundings.py --data-dir DIR --domain north_africa \
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

from acf.awci.obs.store import ObsStore, parse_time  # noqa: E402
from acf.awci.ops.domains import DEFAULT_DOMAINS_PATH, load_domains  # noqa: E402
from acf.awci.ops.store import CubeStore, model_root  # noqa: E402
from acf.awci.ops.verify_sounding import ColumnPair, column_pairs, verify_soundings  # noqa: E402


def pairs_of(root: Path, model: str, domain_name: str, run: str,
             domains_file: Path = DEFAULT_DOMAINS_PATH) -> tuple[list[ColumnPair], dict[str, int], list[float]]:
    domain = load_domains(domains_file)[domain_name]
    cubes = CubeStore(model_root(root, model))
    manifest = cubes.manifest(domain_name, run)
    times = [parse_time(t) for t in manifest["valid_times"]]
    soundings = ObsStore(root, domain_name).soundings(times[0] - timedelta(minutes=1), times[-1] + timedelta(minutes=1))
    pairs, excluded = column_pairs(cubes.dataset(domain_name, run), manifest, soundings, domain)
    return pairs, excluded, list(manifest["levels_hpa"])


def _f(v: float | None, d: int = 2) -> str:
    return "—" if v is None else f"{v:.{d}f}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--domain", default="north_africa")
    parser.add_argument("--runs", required=True)
    parser.add_argument("--models", default="ifs,gfs")
    parser.add_argument("--domains-file", type=Path, default=DEFAULT_DOMAINS_PATH)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    runs = args.runs.split(",")
    report: dict[str, Any] = {"runs": runs, "domain": args.domain, "models": {}}
    for model in args.models.split(","):
        pairs: list[ColumnPair] = []
        excluded: dict[str, int] = {}
        levels: list[float] = []
        for run in runs:
            p, e, levels = pairs_of(args.data_dir, model, args.domain, run, args.domains_file)
            pairs += p
            for k, v in e.items():
                excluded[k] = excluded.get(k, 0) + v
        by_step = {step: verify_soundings([p for p in pairs if p.step == step], {}, levels)
                   for step in sorted({p.step for p in pairs})}
        report["models"][model] = verify_soundings(pairs, excluded, levels) | {
            "by_step": {str(s): {"soundings": r["soundings"], "total": r["total"]} for s, r in by_step.items()}}
    print("| Modèle | Paires | T biais / RMSE (K) | HR biais / RMSE (%) | Vent biais (m/s) | RMSE vect. (m/s) "
          "| Cisaillement biais / RMSE (10⁻³ s⁻¹) | Givrage POD / FAR / ETS |")
    print("|---|---|---|---|---|---|---|---|")
    for model, r in report["models"].items():
        t = r["total"]
        vws = {k: None if t["vws"][k] is None else t["vws"][k] * 1000 for k in ("bias", "rmse")}
        print(f"| {model.upper()} | {r['soundings']} ({t['t']['n']} niv.) | {_f(t['t']['bias'])} / {_f(t['t']['rmse'])} "
              f"| {_f(t['rh']['bias'], 1)} / {_f(t['rh']['rmse'], 1)} | {_f(t['wind_speed']['bias'])} "
              f"| {_f(t['wind_vector_rmse'])} | {_f(vws['bias'])} / {_f(vws['rmse'])} "
              f"| {_f(t['icing']['pod'])} / {_f(t['icing']['far'])} / {_f(t['icing']['ets'])} |")
    for model, r in report["models"].items():
        steps = ", ".join(f"+{s} h : {_f(v['total']['t']['rmse'])} K / {_f(v['total']['wind_vector_rmse'])} m/s "
                          f"({v['soundings']})" for s, v in r["by_step"].items())
        print(f"{model.upper()} RMSE T / vent par échéance (sondages) : {steps}")
    if args.out:
        args.out.write_text(json.dumps(report, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
