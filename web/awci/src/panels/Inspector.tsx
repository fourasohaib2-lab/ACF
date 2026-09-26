import type { PointPayload, Registry } from "../api/types";
import { fr } from "../i18n/fr";
import { flLabel, fmt, stepLabel, utcLabel } from "../lib/format";

const MODULE_LABELS: Record<string, string> = {
  dynamic: "Dynamique", thermodynamic: "Thermodynamique", convective: "Convectif", microphysical: "Microphysique",
  topographic: "Topographique", temporal: "Temporel", confidence: "Confiance",
  wind_topo_interaction: "Vent × relief", conv_thermo_interaction: "Convection × thermodynamique",
};

/** Level and surface quantities shown with their unit; temperatures converted to °C for reading only. */
const LEVEL_ROWS: { key: string; label: string; unit: string; digits: number; convert?: (v: number) => number }[] = [
  { key: "t", label: "Température", unit: "°C", digits: 1, convert: (v) => v - 273.15 },
  { key: "r", label: "Humidité relative (IFS)", unit: "%", digits: 0 },
  { key: "wind_speed", label: "Vent", unit: "m/s", digits: 0 },
  { key: "vertical_shear", label: "Cisaillement vertical", unit: "10⁻³ s⁻¹", digits: 1, convert: (v) => v * 1000 },
  { key: "cat_category", label: "Turbulence CAT (classe 0–3)", unit: "", digits: 0 },
  { key: "icing_potential", label: "Givrage potentiel (0/1)", unit: "", digits: 0 },
  { key: "cloud_fraction", label: "Fraction nuageuse", unit: "octas", digits: 1, convert: (v) => v * 8 },
];
const SURFACE_ROWS: { key: string; label: string; unit: string; digits: number; convert?: (v: number) => number }[] = [
  { key: "mucape", label: "MUCAPE", unit: "J/kg", digits: 0 },
  { key: "precip_rate", label: "Précipitations", unit: "mm/h", digits: 1 },
  { key: "tcc", label: "Couverture totale IFS", unit: "octas", digits: 1, convert: (v) => v * 8 },
  { key: "ceiling_m", label: "Plafond (OACI)", unit: "ft", digits: 0, convert: (v) => v / 0.3048 },
  { key: "gust_10m", label: "Rafales à 10 m", unit: "m/s", digits: 0 },
];

interface Props { point: PointPayload | undefined; registry: Registry | undefined }

export function Inspector({ point, registry }: Props) {
  if (!point) return null;
  const below = point.awci === null && point.level_layers.gh === null;
  const parts = Object.entries(point.decomposition).filter((e): e is [string, number] => e[1] !== null)
    .sort((a, b) => b[1] - a[1]);
  const maxPart = Math.max(1, ...parts.map(([, v]) => v));
  const status = (key: string) => point.scientific_status[key] ?? registry?.layers[key]?.status;
  const row = (r: (typeof LEVEL_ROWS)[number], values: Record<string, number | null>) => {
    if (!(r.key in values)) return null;
    const v = values[r.key];
    return (
      <tr key={r.key}>
        <th scope="row">{r.label}</th>
        <td className="num">{v === null || v === undefined ? "—" : fmt(r.convert ? r.convert(v) : v, r.digits, r.unit)}</td>
        <td className="status-cell">{status(r.key) ?? ""}</td>
      </tr>
    );
  };
  const p = point.provenance;
  return (
    <section className="panel inspector" aria-label="Inspecteur de point">
      <h2>Point {fmt(point.lat, 2)}° N · {fmt(point.lon, 2)}° E</h2>
      <p className="panel-note">{flLabel(point.flight_level)} ({point.level_hpa} hPa)</p>
      {below ? <p className="notice">{fr.belowGround}</p> : (
        <>
          <p className="inspector-awci">
            <span className="kpi-value num">{fmt(point.awci, 0)}</span>
            <span>{point.awci_level ?? "—"}</span>
            <span className="status-cell">AWCI : {point.scientific_status.awci ?? "—"}</span>
          </p>
          <p className="panel-note">Calculé sur {fmt(point.present_weight * 100, 0)} % des poids du profil.</p>
          <ul className="bars" aria-label="Décomposition de l'AWCI (points)">
            {parts.map(([k, v]) => (
              <li key={k}>
                <span className="bar-label">{MODULE_LABELS[k] ?? k}</span>
                <span className="bar-track"><span className="bar-fill" style={{ width: `${(v / maxPart) * 100}%` }} /></span>
                <span className="num">{fmt(v, 1)}</span>
              </li>
            ))}
          </ul>
          {point.missing_inputs.length > 0 && (
            <p className="panel-note">Entrées non disponibles : {point.missing_inputs.map((m) => `${m} (${MODULE_LABELS[m] ?? m})`).join(", ")}.</p>
          )}
        </>
      )}
      <table className="values-table">
        <thead><tr><th scope="col">Grandeur</th><th scope="col">Valeur</th><th scope="col">Statut</th></tr></thead>
        <tbody>
          {LEVEL_ROWS.map((r) => row(r, point.level_layers))}
          {SURFACE_ROWS.map((r) => row(r, point.surface_layers ?? {}))}
        </tbody>
      </table>
      <p className="provenance">
        Run {p.run}{p.step !== null ? ` · ${stepLabel(p.step)}` : ""}{p.valid_time ? ` · valide ${utcLabel(p.valid_time)}` : ""} · {p.attribution}
      </p>
    </section>
  );
}
