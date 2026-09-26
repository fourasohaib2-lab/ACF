import type { ComparePoint } from "../api/types";
import { fmt, utcLabel } from "../lib/format";
import { ErrorBox, Skeleton } from "./StateViews";

interface Props {
  data: ComparePoint | undefined;
  isLoading: boolean;
  error: unknown;
  /** Why no comparison is possible here (no GFS run, step not in both runs, no point), or undefined. */
  unavailable?: string;
  classLabels: string[];
  awciBounds: number[];
}

type Row = { key: string; label: string; format: (v: number | null) => string; event?: (v: number) => boolean; diff?: boolean };
const num = (d: number, unit = "") => (v: number | null) => (v === null ? "—" : `${fmt(v, d)}${unit ? ` ${unit}` : ""}`);
const yesNo = (v: number | null) => (v === null ? "—" : v >= 1 ? "oui" : "non");
const CAT = ["nulle", "légère", "modérée", "modérée à sévère"];
const CONV = ["aucune", "Cu", "TCU", "Cb calvus", "Cb capillatus"];
const code = (labels: string[]) => (v: number | null) => (v === null ? "—" : labels[Math.round(v)] ?? String(v));

const ROWS: Row[] = [
  { key: "awci", label: "AWCI", format: num(0), diff: true },
  { key: "icing_potential", label: "Givrage potentiel", format: yesNo, event: (v) => v >= 1 },
  { key: "cat_category", label: "Turbulence CAT", format: code(CAT), event: (v) => v >= 2 },
  { key: "cloud_fraction", label: "Fraction nuageuse", format: (v) => (v === null ? "—" : `${fmt(v * 8, 1)} octas`), diff: true },
  { key: "wind_speed", label: "Vent", format: num(0, "m/s"), diff: true },
  { key: "t", label: "Température", format: (v) => (v === null ? "—" : `${fmt(v - 273.15, 1)} °C`), diff: true },
  { key: "convective_class", label: "Convection", format: code(CONV), event: (v) => v >= 2 },
  { key: "ceiling_m", label: "Plafond OACI", format: (v) => (v === null ? "aucun" : `${fmt(v / 0.3048, 0)} ft`) },
];

/** IFS and GFS at the inspected point, level and valid time (SP6): values side by side, disagreements said. */
export function ModelAgreement({ data, isLoading, error, unavailable, classLabels, awciBounds }: Props) {
  const shell = (body: React.ReactNode) => <section className="panel" aria-label="Accord des modèles"><h2>Accord des modèles</h2>{body}</section>;
  if (unavailable) return shell(<p className="panel-note">{unavailable}</p>);
  if (error) return shell(<ErrorBox error={error} what="Accord des modèles" />);
  if (isLoading || !data) return shell(<Skeleton height={140} label="Comparaison IFS–GFS" />);
  const ifs = data.models.ifs.values;
  const gfs = data.models.gfs.values;
  const cls = (v: number | null) => (v === null ? null : classLabels[awciBounds.filter((b) => v >= b).length] ?? null);
  const disagreements = ROWS.filter((r) => r.event).filter((r) => {
    const a = ifs[r.key] ?? null;
    const b = gfs[r.key] ?? null;
    return a !== null && b !== null && r.event!(a) !== r.event!(b);
  }).map((r) => `${r.label} : ${r.event!(ifs[r.key]!) ? "IFS seul" : "GFS seul"}`);
  const classA = cls(ifs.awci ?? null);
  const classB = cls(gfs.awci ?? null);
  return shell(
    <>
      <p className="panel-note">Même run ({data.run}), même heure de validité ({utcLabel(data.valid_time)}), niveau {data.level_hpa} hPa,
        maille {fmt(data.lat, 2)}° N, {fmt(data.lon, 2)}° E.</p>
      <p className={disagreements.length || classA !== classB ? "notice" : "panel-note"} role="status">
        {classA === classB ? `Même classe AWCI (${classA ?? "—"})` : `Classes AWCI différentes : IFS ${classA ?? "—"}, GFS ${classB ?? "—"}`}
        {data.awci_diff !== null ? `, écart ${data.awci_diff > 0 ? "+" : ""}${fmt(data.awci_diff, 0)} points (GFS − IFS)` : ""}.
        {disagreements.length ? ` Désaccord sur : ${disagreements.join(" ; ")}.` : " Aucun désaccord sur les dangers."}
      </p>
      <table className="values-table">
        <caption className="visually-hidden">Valeurs IFS et GFS au point</caption>
        <thead><tr><th scope="col">Grandeur</th><th scope="col">IFS</th><th scope="col">GFS</th><th scope="col">Écart</th></tr></thead>
        <tbody>
          {ROWS.map((r) => {
            const a = ifs[r.key] ?? null;
            const b = gfs[r.key] ?? null;
            const differ = r.event && a !== null && b !== null && r.event(a) !== r.event(b);
            return (
              <tr key={r.key} className={differ ? "is-disagreement" : undefined}>
                <th scope="row">{r.label}</th>
                <td className="num">{r.format(a)}</td>
                <td className="num">{r.format(b)}</td>
                <td className="num">{r.diff && a !== null && b !== null ? r.format(b - a + (r.key === "t" ? 273.15 : 0)) : differ ? "désaccord" : ""}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <details>
        <summary>Différences de définition GFS</summary>
        <ul className="plain-list">{Object.entries(data.definition_differences).map(([k, v]) => <li key={k}><code>{k}</code> : {v}</li>)}</ul>
      </details>
      <p className="provenance">{data.models.ifs.attribution} · {data.models.gfs.attribution}</p>
    </>,
  );
}
