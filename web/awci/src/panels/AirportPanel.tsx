import type { AirportDetail, MetarObs } from "../api/types";
import { LineChart } from "../charts/LineChart";
import { ceilingText, convectionText } from "../lib/aero";
import { fmt, stepLabel, utcLabel } from "../lib/format";

const CONVECTIVE_LABELS = ["aucune", "Cu", "TCU", "Cb calvus", "Cb capillatus"];
const MAX_DZ_M = 300;
const GENUS_FR: Record<string, string> = { clear: "ciel clair", indeterminate: "indéterminé" };

interface Props { detail: AirportDetail | undefined; currentStep: number; now: Date; loading: boolean }

const layersText = (o: MetarObs) =>
  o.layers.length ? o.layers.map((l) => `${l.cover}${l.base_ft === null ? "///" : String(l.base_ft / 100).padStart(3, "0")}${l.type ?? ""}`).join(" ")
    : o.cavok ? "CAVOK" : o.no_sig_cloud ?? "—";

function Observed({ o }: { o: MetarObs }) {
  return (
    <>
      <pre className="mono raw-text">{o.raw}</pre>
      <dl className="facts">
        <dt>Heure d'observation</dt><dd>{utcLabel(o.time)}{o.auto ? " · automatique" : ""}</dd>
        <dt>Plafond (OACI)</dt><dd>{ceilingText(o)}</dd>
        <dt>Nuages</dt><dd className="mono">{layersText(o)}{o.vertical_visibility_ft !== null ? ` VV${o.vertical_visibility_ft}` : ""}</dd>
        <dt>Convection</dt><dd>{convectionText(o.convective)}</dd>
        <dt>Visibilité</dt><dd>{o.visibility_m === null ? "—" : o.visibility_m >= 10000 ? "≥ 10 km" : `${fmt(o.visibility_m, 0)} m`}</dd>
        <dt>Temps présent</dt><dd className="mono">{o.weather.join(" ") || "—"}</dd>
        <dt>Catégorie de vol (FAA)</dt><dd>{o.flight_category ?? "—"}</dd>
      </dl>
    </>
  );
}

/** One aerodrome: observation at the valid time on screen, model vs observed over the run, TAF. */
export function AirportPanel({ detail, currentStep, now, loading }: Props) {
  if (!detail) return <section className="panel airport-panel" aria-label="Aérodrome"><h2>Aérodrome</h2><p className="panel-note">{loading ? "Chargement…" : "—"}</p></section>;
  const s = detail.station;
  const pair = detail.pairs.find((p) => p.step === currentStep);
  const point = detail.model.find((m) => m.step === currentStep);
  const future = point ? new Date(point.valid_time).getTime() > now.getTime() : false;
  const dzWarning = detail.dz_m !== null && Math.abs(detail.dz_m) > MAX_DZ_M;
  const byStep = new Map(detail.pairs.map((p) => [p.step, p]));
  const hours = (iso: string) => (new Date(iso).getTime() - new Date(detail.model[0]!.valid_time).getTime()) / 3_600_000;
  const obsCeiling = (o: MetarObs | null | undefined) => (o && o.ceiling_status === "value" ? o.ceiling_ft : null);
  return (
    <section className="panel airport-panel" aria-label="Aérodrome">
      <h2>{s.icao} — {s.name}</h2>
      <p className="panel-note">
        Altitude {fmt(s.elev_m, 0)} m · maille IFS {fmt(detail.grid.lat, 2)}° N {fmt(detail.grid.lon, 2)}° E
        {detail.dz_m !== null ? ` · écart station − surface modèle ${fmt(detail.dz_m, 0)} m` : ""}
      </p>
      {dzWarning && <p className="notice">Écart d'altitude supérieur à {MAX_DZ_M} m : le plafond modèle (au-dessus de la surface du modèle) n'est pas comparable, il est exclu des scores.</p>}
      <div className="airport-grid">
        <div>
          <h3 className="subhead">Observé à la validité {point ? `(${stepLabel(point.step)}, ${utcLabel(point.valid_time)})` : ""}</h3>
          {pair?.observation ? <Observed o={pair.observation} />
            : <p className="panel-note">{future ? "Échéance future : pas encore observée." : "Aucun METAR à ± 30 min de cette validité."}</p>}
          <h3 className="subhead">Modèle au même instant</h3>
          <dl className="facts">
            <dt>Plafond (OACI)</dt><dd>{point?.ceiling_ft == null ? "aucun" : `${fmt(point.ceiling_ft, 0)} ft`}</dd>
            <dt>Convection</dt><dd>{point?.convective_class == null ? "—" : CONVECTIVE_LABELS[point.convective_class] ?? "—"}</dd>
            <dt>Genre, étage bas</dt><dd>{point?.genus_low ? GENUS_FR[point.genus_low] ?? point.genus_low : "—"}</dd>
          </dl>
        </div>
        <div>
          <LineChart yLabel="Plafond (ft)" format={(v) => fmt(v, 0)} yDomain={[0, 5000]} xCurrent={point ? hours(point.valid_time) : undefined}
            xFormat={(x) => `+${fmt(x, 0)} h`}
            series={[
              { id: "obs", label: "Plafond observé (METAR)", color: "var(--series-1)",
                points: detail.model.map((m) => ({ x: hours(m.valid_time), y: obsCeiling(byStep.get(m.step)?.observation) })) },
              { id: "model", label: "Plafond modèle", color: "var(--series-2)",
                points: detail.model.map((m) => ({ x: hours(m.valid_time), y: m.ceiling_ft })) },
            ]} />
          <p className="panel-note">Sous 5000 ft seulement ; un trou signifie aucun plafond ou pas d'observation (pas d'interpolation).</p>
        </div>
      </div>
      <table className="values-table pairs-table">
        <caption className="visually-hidden">Modèle et observation par échéance</caption>
        <thead><tr><th scope="col">Validité</th><th scope="col">Plafond obs.</th><th scope="col">Plafond modèle</th>
          <th scope="col">Convection obs.</th><th scope="col">Convection modèle</th></tr></thead>
        <tbody>
          {detail.model.map((m) => {
            const p = byStep.get(m.step);
            return (
              <tr key={m.step} aria-current={m.step === currentStep ? "true" : undefined}>
                <th scope="row">{stepLabel(m.step)} · {utcLabel(m.valid_time)}</th>
                <td>{p?.observation ? ceilingText(p.observation) : "—"}</td>
                <td className="num">{m.ceiling_ft === null ? "aucun" : `${fmt(m.ceiling_ft, 0)} ft`}</td>
                <td>{p?.observation ? convectionText(p.observation.convective) : "—"}</td>
                <td>{m.convective_class === null ? "—" : CONVECTIVE_LABELS[m.convective_class] ?? "—"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <h3 className="subhead">TAF</h3>
      {detail.taf ? (
        <>
          <p className="panel-note">Dernier TAF reçu : émis {detail.taf.issued ? utcLabel(detail.taf.issued) : "—"} · valide {utcLabel(detail.taf.valid_from)} → {utcLabel(detail.taf.valid_to)}</p>
          {point && !(detail.taf.valid_from <= point.valid_time.replace("+00:00", "Z") && point.valid_time.replace("+00:00", "Z") < detail.taf.valid_to) && (
            <p className="notice">Ce TAF ne couvre pas la validité affichée ({utcLabel(point.valid_time)}) : seul le dernier TAF est conservé.</p>
          )}
          <pre className="mono raw-text">{detail.taf.raw}</pre>
        </>
      ) : <p className="panel-note">Aucun TAF pour cet aérodrome.</p>}
      <p className="provenance">Observations : {detail.attribution} · Modèle : {detail.model_attribution ?? "—"} · diagnostics HYPOTHESIS</p>
    </section>
  );
}
