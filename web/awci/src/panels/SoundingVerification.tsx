import type { ContinuousScore, ScoreTable, SoundingLevelScores, SoundingVerification as Report } from "../api/types";
import { LineKey, VerticalScoreProfile, type ProfileSeries } from "../charts/VerticalScoreProfile";
import { scoreText } from "../lib/aero";
import { fmt, utcLabel } from "../lib/format";
import { ErrorBox, Skeleton } from "./StateViews";

export interface ModelReport { label: string; color: string; report: Report | undefined; isLoading: boolean; error: unknown }
interface Props { models: ModelReport[] }

const EXCLUSIONS: Record<string, string> = {
  no_step_at_nominal_time: "sondages sans échéance du run à leur heure nominale",
  outside_domain: "sondages hors du domaine",
};
const VWS_SCALE = 1000; // 1/s -> 10^-3 s^-1 (m/s per km)
const plural = (n: number, word: string) => `${n} ${word}${n > 1 ? "s" : ""}`;
const num = (v: number | null | undefined, d = 1) => (v === null || v === undefined ? "—" : fmt(v, d));

type Pick = (l: SoundingLevelScores) => number | null;
const series = (models: ModelReport[], bias: Pick, rmse: Pick, rmseLabel = "RMSE"): ProfileSeries[] =>
  models.flatMap((m) => (m.report ? [
    { label: `${m.label} biais`, color: m.color, values: m.report.levels.map(bias) },
    { label: `${m.label} ${rmseLabel}`, color: m.color, dashed: true, values: m.report.levels.map(rmse) },
  ] : []));

function ContinuousCells({ s, scale = 1, d = 1 }: { s: ContinuousScore; scale?: number; d?: number }) {
  return <><td className="num">{num(s.bias === null ? null : s.bias * scale, d)}</td>
    <td className="num">{num(s.rmse === null ? null : s.rmse * scale, d)}</td><td className="num">{s.n}</td></>;
}

function IcingRow({ label, t }: { label: string; t: ScoreTable }) {
  return (
    <tr>
      <th scope="row">{label}</th>
      <td className="num">{t.a}</td><td className="num">{t.b}</td><td className="num">{t.c}</td><td className="num">{t.d}</td>
      <td className="num">{scoreText(t.pod)}</td><td className="num">{scoreText(t.far)}</td>
      <td className="num">{scoreText(t.bias)}</td><td className="num">{scoreText(t.ets)}</td>
      <td>{t.n === 0 ? "aucun niveau" : t.sufficient ? "" : "échantillon insuffisant"}</td>
    </tr>
  );
}

/** Model column against radiosondes (SP7): bias and RMSE profiles, totals and the icing-diagnostic contingency. */
export function SoundingVerification({ models }: Props) {
  const label = "Validation contre les radiosondages";
  const failed = models.find((m) => m.error);
  if (failed) return <section className="sounding-verification" aria-label={label}><ErrorBox error={failed.error} what={`Radiosondages ${failed.label}`} /></section>;
  if (models.some((m) => m.isLoading)) return <section className="sounding-verification" aria-label={label}><Skeleton height={220} label="Radiosondages" /></section>;
  const ready = models.filter((m): m is ModelReport & { report: Report } => !!m.report);
  const first = ready[0]?.report;
  if (!first || ready.every((m) => m.report.soundings === 0)) {
    return (
      <section className="sounding-verification" aria-label={label}>
        <h3 className="subhead">Radiosondages</h3>
        <p className="panel-note">Aucun radiosondage archivé aux heures de validité de ce run
          {first ? ` (${plural(first.stations_known, "station")} ${first.stations_known > 1 ? "connues" : "connue"} sur le domaine)` : ""}. Les sondages s'archivent avec
          <code> acf-awci-obs --soundings</code> ou <code>acf-awci-auto --soundings</code>.</p>
      </section>
    );
  }
  const levels = first.levels.map((l) => l.level_hpa);
  return (
    <section className="sounding-verification" aria-label={label}>
      <h3 className="subhead">Radiosondages : colonne du modèle contre les sondages</h3>
      <p className="panel-note">
        {ready.map((m) => `${m.label} : ${plural(m.report.soundings, "sondage")}, ${plural(m.report.stations, "station")}`).join(" · ")}
        {" "}sur {plural(first.stations_known, "station")} {first.stations_known > 1 ? "connues" : "connue"} · sondages de 00 et 12 UTC appariés à l'échéance de même heure, maille la plus
        proche du lâcher, niveaux standard tels que mesurés (sans interpolation verticale).
      </p>
      <p className="notice">Dérive du ballon négligée (quelques dizaines de km en altitude) ; maille de 25 km contre une mesure
        ponctuelle. Biais = modèle − observation.</p>
      <p className="chart-legend sounding-legend">
        {ready.map((m) => <span key={m.label}><LineKey color={m.color} />{m.label}</span>)}
        <span><LineKey color="var(--text-2)" />biais</span>
        <span><LineKey color="var(--text-2)" dashed />RMSE (vent : RMSE vectorielle)</span>
      </p>
      <div className="sounding-profiles">
        <VerticalScoreProfile title="Température" unit="K" levels={levels} legend={false}
                              series={series(ready, (l) => l.t.bias, (l) => l.t.rmse)} />
        <VerticalScoreProfile title="Humidité relative (eau)" unit="%" levels={levels} digits={0} legend={false}
                              series={series(ready, (l) => l.rh.bias, (l) => l.rh.rmse)} />
        <VerticalScoreProfile title="Vent" unit="m/s" levels={levels} legend={false}
                              series={series(ready, (l) => l.wind_speed.bias, (l) => l.wind_vector_rmse, "RMSE vect.")} />
      </div>
      <div className="table-scroll"><table className="values-table scores-table">
        <caption>Scores sur toute la colonne</caption>
        <thead>
          <tr><th scope="col" rowSpan={2}>Modèle</th><th scope="colgroup" colSpan={3}>T (K)</th><th scope="colgroup" colSpan={3}>HR eau (%)</th>
            <th scope="colgroup" colSpan={3}>Vitesse du vent (m/s)</th><th scope="col" rowSpan={2} title="√(Δu² + Δv²)">RMSE vect. (m/s)</th>
            <th scope="colgroup" colSpan={3}>Cisaillement vertical (10⁻³ s⁻¹)</th></tr>
          <tr>{[0, 1, 2, 3].flatMap((g) => ["biais", "RMSE", "n"].map((h) => <th key={`${g}${h}`} scope="col">{h}</th>))}</tr>
        </thead>
        <tbody>
          {ready.map((m) => (
            <tr key={m.label}>
              <th scope="row">{m.label}</th>
              <ContinuousCells s={m.report.total.t} d={2} /><ContinuousCells s={m.report.total.rh} />
              <ContinuousCells s={m.report.total.wind_speed} /><td className="num">{num(m.report.total.wind_vector_rmse)}</td>
              <ContinuousCells s={m.report.total.vws} scale={VWS_SCALE} d={2} />
            </tr>
          ))}
        </tbody>
      </table></div>
      <div className="table-scroll"><table className="values-table scores-table">
        <caption>Givrage potentiel : diagnostic sur la colonne du modèle contre le même diagnostic sur le profil observé</caption>
        <thead><tr>
          <th scope="col">Modèle</th><th scope="col" title="succès">a</th><th scope="col" title="fausses alertes">b</th>
          <th scope="col" title="non-détections">c</th><th scope="col" title="rejets corrects">d</th>
          <th scope="col">POD</th><th scope="col">FAR</th><th scope="col">Biais</th><th scope="col">ETS</th><th scope="col">Remarque</th>
        </tr></thead>
        <tbody>{ready.map((m) => <IcingRow key={m.label} label={m.label} t={m.report.total.icing} />)}</tbody>
      </table></div>
      <ul className="plain-list">{Object.entries(first.exclusions).filter(([k, n]) => k in EXCLUSIONS && n > 0)
        .map(([k, n]) => <li key={k}><span className="num">{n}</span> {EXCLUSIONS[k]}</li>)}</ul>
      <details>
        <summary>Définitions et limites</summary>
        <p className="panel-note">Biais = moyenne(modèle − observation), RMSE = √moyenne((modèle − observation)²), n = paires de niveaux.
          Humidité relative sur l'eau : modèle calculé depuis q, T et p ; observation telle que publiée par l'University of Wyoming.
          Vent observé u = −V sin(dd), v = −V cos(dd). Cisaillement |ΔV|/Δz entre niveaux voisins, même définition que le modèle,
          Δz tiré du géopotentiel observé.</p>
        <p className="panel-note">Le givrage n'est pas observé : la référence est le diagnostic ACF (T entre −20 et 0 °C et HR ≥ 70 %)
          appliqué au profil mesuré. Ce tableau valide donc les entrées du diagnostic, pas le givrage réel. L'indice de turbulence
          d'Ellrod exige la déformation horizontale, qu'un sondage ne mesure pas : seul son terme de cisaillement vertical est validé.
          Les niveaux d'un même sondage ne sont pas indépendants : aucun intervalle de confiance n'est donné.</p>
      </details>
      <p className="provenance">Observé : {first.observed} · Prévu : {ready.map((m) => m.report.model).join(", ")} · calculé {utcLabel(first.generated_at)}</p>
    </section>
  );
}
