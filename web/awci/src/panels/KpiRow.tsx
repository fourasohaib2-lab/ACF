import type { Summary } from "../api/types";
import { Gauge } from "../charts/Gauge";
import { fr } from "../i18n/fr";
import { fmt } from "../lib/format";
import { StatusBadge } from "./Badge";

interface Card { key: keyof Summary & string; title: string; layer: string; unit: string; digits: number; scale?: number; note?: (s: Summary) => string }

const CARDS: Card[] = [
  { key: "turbulence_area_pct", title: "Turbulence CAT", layer: "cat_category", unit: "%", digits: 1, note: () => "aire ≥ modérée au niveau" },
  { key: "convection_area_pct", title: "Convection", layer: "mucape", unit: "%", digits: 1,
    note: (s) => `MUCAPE ≥ 1 000 J/kg · max ${fmt(s.mucape_max, 0, "J/kg")}` },
  { key: "icing_area_pct", title: "Givrage", layer: "icing_potential", unit: "%", digits: 1, note: () => "aire au niveau" },
  { key: "shear_p95", title: "Cisaillement vertical", layer: "vertical_shear", unit: "10⁻³ s⁻¹", digits: 1, scale: 1000, note: () => "P95 au niveau" },
  { key: "low_ceiling_area_pct", title: "Plafond < 1000 ft", layer: "ceiling_m", unit: "%", digits: 1, note: () => "définition OACI" },
  { key: "cb_area_pct", title: "Cb", layer: "convective_class", unit: "%", digits: 1, note: () => "aire, diagnostic modèle" },
];

interface Props { summary: Summary | undefined; classIndex: number | null; onSelectLayer: (layer: string) => void }

/** Domain KPI row (/summary): area-weighted percentages and percentiles, each card opens its map layer. */
export function KpiRow({ summary, classIndex, onSelectLayer }: Props) {
  return (
    <section className="kpi-row" aria-label="Indicateurs du domaine">
      <button type="button" className="kpi-card kpi-gauge" onClick={() => onSelectLayer("awci")} aria-label="AWCI P95 du domaine">
        <span className="kpi-title">AWCI P95</span>
        <Gauge value={summary?.awci_p95 ?? null} classIndex={classIndex} label={summary?.awci_class ?? null} />
        <span className="kpi-class">{summary?.awci_class ?? "—"}</span>
      </button>
      {CARDS.map((c) => {
        const raw = summary?.[c.key] as number | null | undefined;
        const value = raw === null || raw === undefined ? null : raw * (c.scale ?? 1);
        return (
          <button type="button" key={c.key} className="kpi-card" onClick={() => onSelectLayer(c.layer)}
                  aria-label={`${c.title} : ${value === null ? fr.unavailable : fmt(value, c.digits, c.unit)}`}>
            <span className="kpi-title">{c.title}</span>
            <span className="kpi-value num">{value === null ? "—" : <>{fmt(value, c.digits)}<span className="kpi-unit"> {c.unit}</span></>}</span>
            <span className="kpi-note">{summary && value !== null ? c.note?.(summary) : fr.unavailable}</span>
            <StatusBadge value={summary?.badges[c.key]} />
          </button>
        );
      })}
    </section>
  );
}
