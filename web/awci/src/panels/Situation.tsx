import type { Badge, Meta, Summary } from "../api/types";
import { flLabel, fmt, utcLabel } from "../lib/format";
import { StatusBadge } from "./Badge";

const HAZARDS: { key: string; label: string }[] = [
  { key: "turbulence_area_pct", label: "Turbulence en air clair" },
  { key: "cb_area_pct", label: "Cumulonimbus" },
  { key: "convection_area_pct", label: "Convection (MUCAPE)" },
  { key: "icing_area_pct", label: "Givrage" },
  { key: "shear_p95", label: "Cisaillement vertical" },
  { key: "low_ceiling_area_pct", label: "Plafonds bas" },
  { key: "heavy_precip_area_pct", label: "Précipitations fortes" },
];
const RANK: Record<string, number> = { critical: 3, serious: 2, attention: 1, ok: 0 };

interface Props { summary: Summary | undefined; meta: Meta | undefined; step: number | undefined; domainLabel: string }

/** Current situation from /summary: class of the domain P95, hazards above their badge, main altitude. */
export function Situation({ summary, meta, step, domainLabel }: Props) {
  const hazards = HAZARDS.map((h) => ({ ...h, badge: summary?.badges[h.key] as Badge | undefined }))
    .filter((h) => h.badge && h.badge !== "ok").sort((a, b) => RANK[b.badge!]! - RANK[a.badge!]!);
  const levels = summary?.awci_p95_by_level.filter((l) => l.awci_p95 !== null) ?? [];
  const main = levels.reduce<(typeof levels)[number] | undefined>((best, l) => (!best || l.awci_p95! > best.awci_p95! ? l : best), undefined);
  const si = meta && step !== undefined ? meta.steps.indexOf(step) : -1;
  return (
    <section className="panel" aria-label="Situation actuelle">
      <h2>Situation actuelle</h2>
      <dl className="facts">
        <dt>Classe AWCI (P95)</dt><dd>{summary?.awci_class ?? "—"} <span className="num">({fmt(summary?.awci_p95, 0)})</span></dd>
        <dt>Zone</dt><dd>{domainLabel}</dd>
        <dt>Altitude la plus complexe</dt>
        <dd>{main ? `${flLabel(main.flight_level)} (${main.level_hpa} hPa), P95 ${fmt(main.awci_p95, 0)}` : "—"}</dd>
        <dt>Validité</dt><dd>{si >= 0 && meta ? utcLabel(meta.valid_times[si]!) : "—"}</dd>
      </dl>
      <h3 className="subhead">Dangers au-dessus de leur seuil</h3>
      {hazards.length ? (
        <ul className="hazard-list">{hazards.map((h) => <li key={h.key}><StatusBadge value={h.badge} />{h.label}</li>)}</ul>
      ) : <p className="panel-note">{summary ? "Aucun danger au-dessus de son seuil d'attention." : "—"}</p>}
      <p className="panel-note">Seuils des badges : choix ACF, statut HYPOTHESIS (voir API et registre).</p>
    </section>
  );
}
