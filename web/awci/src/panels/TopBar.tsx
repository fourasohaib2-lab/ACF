import { ChevronLeft, ChevronRight, Clock4 } from "lucide-react";
import type { ReactNode } from "react";
import type { Domain, Meta, RunInfo } from "../api/types";
import { fr } from "../i18n/fr";
import { flLabel, stepLabel, utcLabel } from "../lib/format";
import type { ViewState } from "../state/view";

interface Props {
  domains: Domain[];
  domain: string;
  runs: RunInfo[];
  run: string;
  meta: Meta | undefined;
  step: number | undefined;
  level: number | undefined;
  now: Date;
  onChange: (patch: Partial<ViewState>) => void;
  onPrev: () => void;
  onNext: () => void;
  onNow: () => void;
  status: ReactNode;
}

export function TopBar({ domains, domain, runs, run, meta, step, level, now, onChange, onPrev, onNext, onNow, status }: Props) {
  const si = meta && step !== undefined ? meta.steps.indexOf(step) : -1;
  return (
    <header className="topbar">
      <div className="brand">
        <span className="brand-title">{fr.appTitle}</span>
        <span className="brand-sub">{fr.appSubtitle}</span>
      </div>
      <div className="topbar-controls">
        <label className="field">
          <span>Domaine</span>
          <select value={domain} onChange={(e) => onChange({ domain: e.target.value, run: undefined, step: undefined, lat: undefined, lon: undefined })}>
            {domains.map((d) => <option key={d.name} value={d.name}>{d.label}</option>)}
          </select>
        </label>
        <label className="field">
          <span>Run</span>
          <select value={run} onChange={(e) => onChange({ run: e.target.value, step: undefined })}>
            {runs.map((r) => (
              <option key={r.run} value={r.run} disabled={r.status === "failed"}>
                {utcLabel(r.run_time)}{r.status === "partial" ? " (partiel)" : r.status === "failed" ? " (échec)" : ""}
              </option>
            ))}
          </select>
        </label>
        <div className="field">
          <span>Validité</span>
          <div className="stepper">
            <button type="button" className="icon-button" onClick={onPrev} aria-label="Échéance précédente"><ChevronLeft size={16} aria-hidden="true" /></button>
            <span className="stepper-value num" aria-live="polite">
              {si >= 0 && meta ? `${utcLabel(meta.valid_times[si]!)} (${stepLabel(step!)})` : "—"}
            </span>
            <button type="button" className="icon-button" onClick={onNext} aria-label="Échéance suivante"><ChevronRight size={16} aria-hidden="true" /></button>
            <button type="button" className="text-button" onClick={onNow}>{fr.now}</button>
          </div>
        </div>
        <label className="field">
          <span>Niveau</span>
          <select value={level ?? ""} onChange={(e) => onChange({ level: Number(e.target.value) })} disabled={!meta}>
            {meta?.levels_hpa.map((p, i) => <option key={p} value={p}>{p} hPa · {flLabel(meta.flight_levels[i]!)}</option>)}
          </select>
        </label>
        <div className="field">
          <span>Modèle</span>
          <span className="field-static">{fr.model}</span>
        </div>
      </div>
      <div className="topbar-right">
        {status}
        <span className="clock num" aria-label="Heure UTC courante"><Clock4 size={14} aria-hidden="true" />
          {`${String(now.getUTCHours()).padStart(2, "0")}:${String(now.getUTCMinutes()).padStart(2, "0")} UTC`}</span>
      </div>
    </header>
  );
}
