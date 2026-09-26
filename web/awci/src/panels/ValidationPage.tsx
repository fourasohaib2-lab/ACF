import type { ScoreTable, Verification } from "../api/types";
import { scoreText } from "../lib/aero";
import { fmt, utcLabel } from "../lib/format";
import { ErrorBox, Skeleton } from "./StateViews";

export const EVENT_LABELS: Record<string, string> = {
  ceiling_below_500ft: "Plafond < 500 ft (LIFR, FAA)",
  ceiling_below_1000ft: "Plafond < 1000 ft (IFR, FAA)",
  ceiling_below_1500ft: "Plafond < 1500 ft (VMC en zone de contrôle, OACI Annexe 2)",
  convective: "Convection (TCU/CB observés ; modèle classe ≥ TCU)",
};
const EXCLUSIONS: Record<string, string> = {
  no_report_within_tolerance: "pas de METAR à ± 30 min",
  not_yet_observed: "échéance pas encore observée",
  undecodable: "METAR non décodable",
  elevation_mismatch: "écart d'altitude station/modèle > 300 m (plafond)",
  ceiling_unknown: "plafond observé inconnu (///)",
  convection_unknown: "convection observée inconnue (station automatique)",
};

function Row({ label, t }: { label: string; t: ScoreTable }) {
  return (
    <tr>
      <th scope="row">{label}</th>
      <td className="num">{t.n}</td><td className="num">{t.observed_events}</td>
      <td className="num">{t.a}</td><td className="num">{t.b}</td><td className="num">{t.c}</td><td className="num">{t.d}</td>
      <td className="num">{scoreText(t.pod)}</td><td className="num">{scoreText(t.far)}</td><td className="num">{scoreText(t.csi)}</td>
      <td className="num">{scoreText(t.bias)}</td><td className="num">{scoreText(t.ets)}</td>
      <td>{t.n === 0 ? "aucune paire" : t.sufficient ? "" : "échantillon insuffisant"}</td>
    </tr>
  );
}

interface Props { verification: Verification | undefined; isLoading: boolean; error: unknown }

/** Verification of the run's ceiling and convection against METAR: contingency tables and standard scores. */
export function ValidationPage({ verification: v, isLoading, error }: Props) {
  if (error) return <section className="panel validation-page" aria-label="Validation"><ErrorBox error={error} what="Validation" /></section>;
  if (isLoading || !v) return <section className="panel validation-page" aria-label="Validation"><Skeleton height={300} label="Calcul de la validation" /></section>;
  return (
    <section className="panel validation-page" aria-label="Validation">
      <h2>Validation du run {v.run} contre les METAR</h2>
      <p className="panel-note">
        Validités {utcLabel(v.valid_from)} → {utcLabel(v.valid_to)} · {v.pairs} paires · {v.stations.with_pairs} stations sur {v.stations.total}
        {v.observations_ingested_at ? ` · observations ingérées ${utcLabel(v.observations_ingested_at)}` : ""}
      </p>
      <p className="notice">
        Diagnostics nuageux au statut HYPOTHESIS. Maille IFS 25 km contre observation ponctuelle, METAR à ± {v.parameters.tolerance_min} min :
        ces scores mesurent l'accord du diagnostic avec les aérodromes, pas une vérité ponctuelle.
      </p>
      {Object.entries(v.events).map(([key, e]) => (
        <table key={key} className="values-table scores-table">
          <caption>{EVENT_LABELS[key] ?? key}</caption>
          <thead><tr>
            <th scope="col">Échéance</th><th scope="col">n</th><th scope="col">Obs.</th>
            <th scope="col" title="succès">a</th><th scope="col" title="fausses alertes">b</th><th scope="col" title="manqués">c</th><th scope="col" title="rejets corrects">d</th>
            <th scope="col">POD</th><th scope="col">FAR</th><th scope="col">CSI</th><th scope="col">Biais</th><th scope="col">ETS</th><th scope="col">Remarque</th>
          </tr></thead>
          <tbody>
            {e.by_lead.map((b) => <Row key={b.lead} label={b.lead} t={b} />)}
            <Row label="Total" t={e.total} />
          </tbody>
        </table>
      ))}
      <h3 className="subhead">Base du plafond</h3>
      <p>{v.ceiling_base_error_ft.n
        ? `Erreur moyenne ${fmt(v.ceiling_base_error_ft.mean_error, 0)} ft, erreur absolue moyenne ${fmt(v.ceiling_base_error_ft.mae, 0)} ft (n = ${v.ceiling_base_error_ft.n}, modèle − observé, deux plafonds sous 5000 ft).`
        : "Aucune paire avec deux plafonds sous 5000 ft."}</p>
      <h3 className="subhead">Exclusions</h3>
      <ul className="plain-list">{Object.entries(v.exclusions).map(([k, n]) => <li key={k}><span className="num">{n}</span> {EXCLUSIONS[k] ?? k}</li>)}</ul>
      <details>
        <summary>Définitions et paramètres</summary>
        <p className="panel-note">a succès, b fausses alertes, c manqués, d rejets corrects. POD = a/(a+c) ; FAR = b/(a+b) ; CSI = a/(a+b+c) ;
          biais = (a+b)/(a+c) ; ETS = (a − a_r)/(a+b+c − a_r), a_r = (a+b)(a+c)/n (Jolliffe et Stephenson, 2012). Un score au dénominateur nul
          est « — » ; moins de {v.parameters.min_observed_events} événements observés : échantillon insuffisant.</p>
        <p className="panel-note">Point de grille le plus proche ; METAR/SPECI le plus proche à ± {v.parameters.tolerance_min} min ;
          stations à plus de {v.parameters.max_elevation_diff_m} m de la surface modèle exclues du plafond ({v.parameters.status}).</p>
      </details>
      <p className="provenance">Observé : {v.observed} · Prévu : {v.forecast} · calculé {utcLabel(v.generated_at)}</p>
    </section>
  );
}
