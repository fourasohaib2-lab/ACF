import type { RunInfo } from "../api/types";
import { ageLabel, utcLabel } from "../lib/format";

/** "Latest updates" of the mockup: the runs actually ingested, with their completeness. */
export function LatestRuns({ runs, now }: { runs: RunInfo[]; now: Date }) {
  if (!runs.length) return null;
  return (
    <section className="panel" aria-label="Derniers runs">
      <h2>Derniers runs ingérés</h2>
      <ul className="runs-list">
        {runs.slice(0, 6).map((r) => (
          <li key={r.run}>
            <span className="num">{utcLabel(r.run_time)}</span>
            <span>{r.status === "complete" ? "complet" : r.status === "partial" ? `partiel (${r.missing_steps.length} manquante(s))` : "échec"}</span>
            <span className="panel-note">{r.ingested_at ? `ingéré ${ageLabel(r.ingested_at, now)}` : ""}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
