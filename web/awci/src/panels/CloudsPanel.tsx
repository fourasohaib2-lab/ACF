import type { CloudsPayload, CloudsSeries } from "../api/types";
import { fr } from "../i18n/fr";
import { FT_PER_M, flLabel, fmt } from "../lib/format";
import { CATEGORICAL } from "../theme/palette";
import { familyColor, GenusTimeline } from "./GenusTimeline";

const ETAGE = { low: "étage bas", mid: "étage moyen", high: "étage haut" } as const;
const H = 320;
const W = 300;
const PAD = { t: 8, b: 22, l: 52 };

interface Props { clouds: CloudsPayload | undefined; series: CloudsSeries | undefined; currentStep: number; unavailable?: boolean }

/** Cloud layers at a point on one altitude axis (km AMSL, ft): model diagnostics, never observations. */
export function CloudsPanel({ clouds, series, currentStep, unavailable = false }: Props) {
  if (unavailable) {
    return <section className="panel" aria-label="Nuages"><h2>Nuages</h2><p className="panel-note">{fr.cloudsNotAvailable}</p></section>;
  }
  if (!clouds) return null;
  const elev = clouds.elevation_m ?? 0;
  const tops = clouds.layers.map((l) => l.top_amsl_m);
  const zMax = Math.max(6000, ...tops.map((t) => t + 500));
  const sy = (z: number) => PAD.t + (1 - z / zMax) * (H - PAD.t - PAD.b);
  const ticksKm = Array.from({ length: Math.floor(zMax / 3000) + 1 }, (_, i) => i * 3);
  const conv = clouds.convective;
  return (
    <section className="panel clouds-panel" aria-label="Nuages">
      <h2>Nuages au point</h2>
      <p className="caveat">{fr.cloudsCaveat}</p>
      <div className="clouds-body">
        <svg viewBox={`0 0 ${W} ${H}`} className="chart-svg clouds-column" role="img"
             aria-label={`Colonne nuageuse : ${clouds.layers.length ? clouds.layers.map((l) => l.genus).join(", ") : "ciel clair"}`}>
          <defs>
            <pattern id="conv-hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
              <rect width="6" height="6" fill="none" /><line x1="0" y1="0" x2="0" y2="6" stroke={CATEGORICAL[1]} strokeWidth="3" />
            </pattern>
          </defs>
          {ticksKm.map((km) => (
            <g key={km}><line x1={PAD.l} x2={W} y1={sy(km * 1000)} y2={sy(km * 1000)} className="chart-grid" />
              <text x={PAD.l - 4} y={sy(km * 1000) + 4} textAnchor="end" className="chart-tick">{km} km</text></g>
          ))}
          <rect x={PAD.l} y={sy(elev)} width={W - PAD.l} height={Math.max(0, H - PAD.b - sy(elev))} fill="var(--surface-3)" />
          {clouds.layers.map((l, i) => {
            const base = l.base_agl_m + elev;
            const y0 = sy(l.top_amsl_m);
            const y1 = sy(base);
            const convective = l.kind === "convective";
            return (
              <g key={i}>
                <rect x={PAD.l + (convective ? 150 : 8)} width={convective ? 70 : 132} y={Math.min(y0, y1 - 4)} height={Math.max(4, y1 - y0)}
                      fill={convective ? "url(#conv-hatch)" : familyColor(l.genus) ?? "var(--axis)"} opacity={convective ? 1 : 0.35 + 0.08 * (l.oktas ?? 0)}
                      stroke={convective ? CATEGORICAL[1] : "none"} />
                <text x={PAD.l + (convective ? 150 : 12)} y={Math.min(y0, y1 - 4) - 3} className="cloud-label">{l.genus}</text>
              </g>
            );
          })}
          {clouds.ceiling_m !== null && (
            <g><line x1={PAD.l} x2={W} y1={sy(clouds.ceiling_m + elev)} y2={sy(clouds.ceiling_m + elev)} className="ceiling-line" />
              <text x={W - 2} y={sy(clouds.ceiling_m + elev) - 3} textAnchor="end" className="cloud-label">plafond</text></g>
          )}
        </svg>
        <div className="clouds-facts">
          <p className="metar mono">{clouds.metar}</p>
          <ul className="layer-list-text">
            {clouds.layers.length === 0 && <li>Aucune couche diagnostiquée (ciel clair au sens du modèle).</li>}
            {clouds.layers.map((l, i) => (
              <li key={i}>
                <strong>{[l.genus, ...l.species].join(" ")}</strong>
                {l.kind === "convective"
                  ? ` · convectif, base ${fmt(l.base_ft, 0)} ft sol, sommet ${fmt(l.top_amsl_m, 0)} m (${fmt(l.top_amsl_m * FT_PER_M, 0)} ft)`
                  : ` · ${l.amount} (${l.oktas}/8) · ${l.base_fl !== null ? flLabel(l.base_fl) : "—"}–${l.top_fl !== null ? flLabel(l.top_fl) : "—"}`
                    + ` · base ${fmt(l.base_ft, 0)} ft sol (± ${fmt((l.base_uncertainty_m ?? 0) * FT_PER_M, 0)} ft) · ${l.etage ? ETAGE[l.etage] : ""}`}
              </li>
            ))}
          </ul>
          <dl className="facts">
            <dt>Plafond (OACI)</dt><dd>{clouds.ceiling_ft === null ? "pas de plafond" : `${fmt(clouds.ceiling_ft, 0)} ft`}</dd>
            <dt>Convection</dt><dd>{conv.label}{conv.top_temp_k !== null ? `, sommet ${fmt(conv.top_temp_k - 273.15, 0)} °C` : ""}</dd>
            <dt>T sommets (OLR)</dt><dd>{clouds.cloud_top_teff_k === null ? "—" : `${fmt(clouds.cloud_top_teff_k - 273.15, 0)} °C`}</dd>
            <dt>Condensat colonne</dt><dd>{fmt(clouds.column_condensate, 2, "kg/m²")}</dd>
            <dt>Couverture IFS / diagnostic</dt>
            <dd>{fmt((clouds.tcc ?? Number.NaN) * 8, 1)} / {fmt((clouds.cloud_covers?.total_diag ?? Number.NaN) * 8, 1)} octas (écart {fmt(clouds.cloud_cover_bias, 2)})</dd>
            <dt>Cohérence du run</dt><dd>{clouds.run_cloud_status === "degraded" ? "dégradée" : clouds.run_cloud_status === "ok" ? "correcte" : "—"}</dd>
            {clouds.etage_bounds_fl && <><dt>Bornes d'étage (σ ECMWF)</dt>
              <dd>{`bas/moyen ${flLabel(clouds.etage_bounds_fl.low_mid)} · moyen/haut ${flLabel(clouds.etage_bounds_fl.mid_high)}`}</dd></>}
          </dl>
        </div>
      </div>
      {series && <GenusTimeline series={series} currentStep={currentStep} />}
      <p className="provenance">{clouds.cloud_profile?.name} {clouds.cloud_profile?.version} · {clouds.provenance?.attribution ?? fr.forecastAttribution}</p>
    </section>
  );
}
