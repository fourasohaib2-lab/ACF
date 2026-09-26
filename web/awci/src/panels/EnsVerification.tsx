import type { BrierScores, EnsVerification as Report } from "../api/types";
import { ReliabilityDiagram } from "../charts/ReliabilityDiagram";
import { fmt, utcLabel } from "../lib/format";
import { ErrorBox, Skeleton } from "./StateViews";

const ENS_EVENT_LABELS: Record<string, string> = {
  ceiling_below_1500ft: "P(plafond < 1500 ft)",
  convective: "P(TCU/Cb réalisé)",
};
const EXCLUSIONS: Record<string, string> = {
  not_an_ens_step: "échéance déterministe sans équivalent ENS (ENS à 6 h)",
  no_ens_member: "aucun membre valide dans la maille",
};
const score = (v: number | null | undefined, d = 3) => (v === null || v === undefined ? "—" : fmt(v, d));

const percent = (v: number) => `${fmt(Math.abs(v) * 100, 0)} %`;

/** Plain reading of the total scores; nothing is said about a sample the scores themselves call insufficient. */
export function reading(s: BrierScores, likeForLike = true): string[] {
  if (!s.sufficient) return [`Moins d'événements observés que le minimum requis (${s.observed_events}) : scores indicatifs seulement.`];
  const out: string[] = [];
  if (s.skill_vs_deterministic !== null) {
    out.push(s.skill_vs_deterministic >= 0
      ? `Erreur de Brier réduite de ${percent(s.skill_vs_deterministic)} par rapport au déterministe sur les mêmes cas.`
      : `Erreur de Brier supérieure de ${percent(s.skill_vs_deterministic)} à celle du déterministe sur les mêmes cas.`);
    if (!likeForLike) out[out.length - 1] += " Profils nuageux différents : cet écart mêle l'apport de l'ensemble et le changement de règles.";
  }
  if (s.bss_climatology !== null) {
    out.push(s.bss_climatology > 0
      ? `Meilleur que la fréquence observée de l'échantillon (BSS ${fmt(s.bss_climatology, 2)}).`
      : `Pas meilleur que la fréquence observée de l'échantillon (BSS ${fmt(s.bss_climatology, 2)}) : probabilités à ne pas utiliser seules.`);
  }
  if (s.mean_probability !== undefined && s.observed_frequency !== undefined && s.observed_frequency > 0) {
    const ratio = s.mean_probability / s.observed_frequency;
    out.push(`Probabilité moyenne ${fmt(ratio, 2)} fois la fréquence observée (${ratio > 1 ? "sur" : "sous"}-prévision en moyenne).`);
  }
  return out;
}

function Row({ label, s }: { label: string; s: BrierScores }) {
  return (
    <tr>
      <th scope="row">{label}</th>
      <td className="num">{s.n}</td><td className="num">{s.observed_events}</td>
      <td className="num">{score(s.observed_frequency)}</td><td className="num">{score(s.mean_probability)}</td>
      <td className="num">{score(s.brier)}</td><td className="num">{score(s.fair_brier)}</td>
      <td className="num">{score(s.brier_deterministic)}</td>
      <td className="num">{score(s.bss_climatology, 2)}</td><td className="num">{score(s.skill_vs_deterministic, 2)}</td>
      <td>{s.n === 0 ? "aucun cas" : s.sufficient ? "" : "échantillon insuffisant"}</td>
    </tr>
  );
}

interface Props { report: Report | undefined; isLoading: boolean; error: unknown; available: boolean }

/** Brier scores and reliability of the ENS probabilities against METAR, next to the deterministic run (SP5b). */
export function EnsVerification({ report: v, isLoading, error, available }: Props) {
  if (error) return <section className="ens-verification" aria-label="Validation de l'ensemble"><ErrorBox error={error} what="Validation de l'ensemble" /></section>;
  if (isLoading) return <section className="ens-verification" aria-label="Validation de l'ensemble"><Skeleton height={200} label="Validation de l'ensemble" /></section>;
  if (!available || !v) {
    return <section className="ens-verification" aria-label="Validation de l'ensemble"><h3 className="subhead">Ensemble ECMWF</h3>
      <p className="panel-note">Pas d'ensemble calculé pour ce run : aucune validation probabiliste.</p></section>;
  }
  return (
    <section className="ens-verification" aria-label="Validation de l'ensemble">
      <h3 className="subhead">Ensemble ECMWF : probabilités contre les METAR</h3>
      <p className="panel-note">Mêmes paires que ci-dessus, aux échéances de l'ensemble ; le déterministe est noté sur ces mêmes paires
        comme une probabilité 0 ou 1. {v.samples} cas.</p>
      {!v.like_for_like && (
        <p className="notice" role="note">
          Profil nuageux {v.cloud_profiles.ens ?? "?"} pour l'ensemble, {v.cloud_profiles.deterministic ?? "?"} pour le déterministe :
          la comparaison de la convection au déterministe n'est pas à règles égales.
        </p>
      )}
      {Object.entries(v.events).map(([key, e]) => (
        <div key={key} className="ens-verif-event">
          <div className="table-scroll"><table className="values-table scores-table">
            <caption>{ENS_EVENT_LABELS[key] ?? key}</caption>
            <thead><tr>
              <th scope="col">Échéance</th><th scope="col">n</th><th scope="col">Obs.</th>
              <th scope="col" title="fréquence observée">Fréq. obs.</th><th scope="col" title="probabilité moyenne prévue">P moy.</th>
              <th scope="col" title="score de Brier de l'ensemble">BS</th><th scope="col" title="Brier corrigé de la taille d'ensemble (Ferro 2014)">BS fair</th>
              <th scope="col" title="Brier du déterministe sur les mêmes paires">BS dét.</th>
              <th scope="col" title="1 − BS / incertitude (climatologie de l'échantillon)">BSS clim.</th>
              <th scope="col" title="1 − BS / BS déterministe">Gain / dét.</th><th scope="col">Remarque</th>
            </tr></thead>
            <tbody>
              {e.by_step.map((s) => <Row key={s.step} label={`+${s.step} h`} s={s} />)}
              <Row label="Total" s={e.total} />
            </tbody>
          </table></div>
          {e.total.n > 0 && (
            <div className="ens-verif-body">
              <ReliabilityDiagram bins={e.total.diagram} climatology={e.total.observed_frequency ?? null}
                                  label={ENS_EVENT_LABELS[key] ?? key} minCases={v.parameters.min_observed_events} />
              <div className="ens-verif-reading">
                <h4>Lecture</h4>
                <ul className="plain-list">{reading(e.total, v.like_for_like).map((line) => <li key={line}>{line}</li>)}</ul>
                <p className="panel-note">Décomposition de Murphy : fiabilité {score(e.total.reliability, 4)}, résolution {score(e.total.resolution, 4)},
                  incertitude {score(e.total.uncertainty, 4)}, résidu de classement {score(e.total.decomposition_residual, 4)}.</p>
              </div>
            </div>
          )}
        </div>
      ))}
      <ul className="plain-list">{Object.entries(v.exclusions).filter(([k]) => k in EXCLUSIONS)
        .map(([k, n]) => <li key={k}><span className="num">{n}</span> {EXCLUSIONS[k]}</li>)}</ul>
      <details>
        <summary>Définitions</summary>
        <p className="panel-note">BS = moyenne de (p − o)² (Brier, 1950). BS fair retranche p(1 − p)/(m − 1) par cas, m membres
          (Ferro, 2014) : il estime le score d'un ensemble infini. BSS clim. = 1 − BS/[ō(1 − ō)], référence la fréquence observée de
          l'échantillon. Gain / dét. = 1 − BS/BS dét. ; positif : l'ensemble fait mieux que le déterministe sur les mêmes paires.
          Décomposition BS = fiabilité − résolution + incertitude (Murphy, 1973), exacte au résidu de classement près (classes de 10 %).</p>
        <p className="panel-note">Les cas ne sont indépendants ni dans l'espace ni dans le temps : aucun intervalle de confiance n'est
          donné ; moins de {v.parameters.min_observed_events} événements observés, échantillon insuffisant.</p>
      </details>
      <p className="provenance">Observé : {v.observed} · Prévu : {v.forecast} · calculé {utcLabel(v.generated_at)}</p>
    </section>
  );
}
