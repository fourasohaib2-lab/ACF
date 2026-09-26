import { AlertTriangle, CheckCircle2, Clock } from "lucide-react";
import type { RunInfo } from "../api/types";
import { fr } from "../i18n/fr";
import { ageLabel, utcLabel } from "../lib/format";

const STALE_HOURS = 18; // spec SP2 §8: a run older than 18 h is flagged

interface Props { run: RunInfo | undefined; cloudStatus: "ok" | "degraded" | null | undefined; now: Date }

/** What data is on screen and how fresh it is: run, completeness, ingestion age, cloud consistency. */
export function DataStatus({ run, cloudStatus, now }: Props) {
  if (!run) return null;
  const ageH = (now.getTime() - new Date(run.run_time).getTime()) / 3_600_000;
  const partial = run.status === "partial";
  return (
    <div className="data-status" aria-label="État des données">
      <span className="data-status-item">
        {partial ? <AlertTriangle size={14} aria-hidden="true" className="status-attention" />
          : <CheckCircle2 size={14} aria-hidden="true" className="status-ok" />}
        Run {utcLabel(run.run_time)} · {partial ? `partiel (${run.missing_steps.length} échéance(s) manquante(s))` : "complet"}
      </span>
      {run.ingested_at && (
        <span className="data-status-item"><Clock size={14} aria-hidden="true" />ingéré {ageLabel(run.ingested_at, now)}</span>
      )}
      {ageH > STALE_HOURS && (
        <span className="data-status-item badge badge-attention"><AlertTriangle size={14} aria-hidden="true" />{fr.staleRun}</span>
      )}
      {cloudStatus === "degraded" && (
        <span className="data-status-item badge badge-attention"><AlertTriangle size={14} aria-hidden="true" />Nuages : cohérence dégradée</span>
      )}
    </div>
  );
}
