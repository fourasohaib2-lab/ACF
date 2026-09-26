import type { EnsPoint, EnsProduct } from "../api/types";
import { fmt, stepLabel, utcLabel } from "../lib/format";

const ROWS: { key: EnsProduct; label: string }[] = [
  { key: "p_awci_high", label: "AWCI ≥ High (niveau)" },
  { key: "p_cloud_bkn", label: "Nuage ≥ 5/8 (niveau)" },
  { key: "p_icing", label: "Givrage potentiel (niveau)" },
  { key: "p_cat_moderate", label: "Turbulence CAT ≥ modérée (niveau)" },
  { key: "p_convection", label: "Convection TCU/Cb réalisée" },
  { key: "p_ceiling_1500ft", label: "Plafond < 1500 ft" },
];
const pct = (v: number | null | undefined) => (v === null || v === undefined ? "—" : `${Math.round(v * 100)} %`);

interface Props { point: EnsPoint | undefined; step: number; deterministicAwci: number | null; unavailable?: boolean }

/**
 * IFS ENS at the selected point and level (spec SP5 §5): probability = share of the members with the event.
 * Replaces the "model agreement" placeholder when the run has an ENS run. A step the ENS did not compute is
 * said so, never borrowed from a neighbouring step.
 */
export function EnsemblePanel({ point, step, deterministicAwci, unavailable = false }: Props) {
  if (unavailable) {
    return (
      <section className="panel" aria-label="Ensemble ECMWF">
        <h2>Ensemble ECMWF</h2>
        <p className="panel-note">Pas d'ensemble pour ce run : lancer acf-awci-ens pour obtenir probabilités et dispersion (50 membres).</p>
      </section>
    );
  }
  if (!point) {
    return (
      <section className="panel" aria-label="Ensemble ECMWF">
        <h2>Ensemble ECMWF</h2>
        <p className="panel-note">Cliquer sur la carte pour les probabilités au point.</p>
      </section>
    );
  }
  const at = point.points.find((p) => p.step === step);
  return (
    <section className="panel" aria-label="Ensemble ECMWF">
      <h2>Ensemble ECMWF</h2>
      <p className="panel-note">{fmt(point.lat, 2)}° N · {fmt(point.lon, 2)}° E · {point.level_hpa} hPa</p>
      {!at || at.missing || !at.probabilities ? (
        <p className="notice">Échéance {stepLabel(step)} pas calculée par l'ensemble (échéances {point.points.filter((p) => !p.missing).map((p) => stepLabel(p.step)).join(", ")}).</p>
      ) : (
        <>
          <p className="panel-note">Valide {utcLabel(at.valid_time)} · {at.members} membres</p>
          <table className="values-table">
            <caption className="visually-hidden">Probabilités de l'ensemble au point</caption>
            <thead><tr><th scope="col">Événement</th><th scope="col">Probabilité</th></tr></thead>
            <tbody>
              {ROWS.map((r) => (
                <tr key={r.key}><th scope="row">{r.label}</th><td className="num">{pct(at.probabilities![r.key])}</td></tr>
              ))}
            </tbody>
          </table>
          <p>AWCI : moyenne {fmt(at.awci_mean, 0)} ± {fmt(at.awci_std, 0)} (écart-type des membres) · Déterministe {fmt(deterministicAwci, 0)}</p>
        </>
      )}
      <p className="provenance">{point.attribution} · probabilité = part des membres ; résolution {Math.round(100 / Math.max(1, at?.members ?? point.members_requested))} %.
        Diagnostics identiques au déterministe (statut HYPOTHESIS).</p>
    </section>
  );
}
