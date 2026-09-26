import type { RouteMeteogram as Payload } from "../api/types";
import { fmt, utcLabel } from "../lib/format";
import { AWCI_CLASS_COLORS } from "../theme/palette";

interface Props {
  meteogram: Payload;
  awciBounds: number[];
  classLabels: string[];
  currentStep: number;
  currentLevel: number;
  onSelect: (step: number, level: number) => void;
}

/** Cell text colour per AWCI class, WCAG AA (≥ 4.5:1) measured: white on the two darkest classes (6.5, 4.7),
 *  dark surface on the others (5.5 to 13.2). */
const TEXT_ON_CLASS = ["#ffffff", "#ffffff", "#0b1220", "#0b1220", "#0b1220", "#0b1220"] as const;
const pct = (v: number | null | undefined) => (v === null || v === undefined ? "—" : `${fmt(v * 100, 0)} %`);
const stepLabel = (s: number) => `+${s} h`;

/**
 * Route meteogram: for every step (columns) and level (rows, highest first), the maximum AWCI along the route,
 * coloured by class. Each cell is a button: it sets the map's step and level. Its label gives the maximum, the
 * median and the share of the route in class ≥ High, icing, CAT ≥ moderate and cloud ≥ 5/8.
 */
export function RouteMeteogram({ meteogram: m, awciBounds, classLabels, currentStep, currentLevel, onSelect }: Props) {
  const order = m.levels_hpa.map((p, li) => ({ p, li, fl: m.flight_levels[li]! })).sort((a, b) => b.fl - a.fl);
  const cls = (v: number) => awciBounds.filter((b) => v >= b).length;
  return (
    <div className="route-meteogram-wrap">
      <table className="route-meteogram">
        <caption>AWCI maximal le long de la route, par échéance et niveau (clic : afficher cette échéance et ce niveau)</caption>
        <thead>
          <tr><th scope="col">Niveau</th>{m.steps.map((s) => <th key={s.step} scope="col" className={s.step === currentStep ? "is-current" : undefined}
            title={utcLabel(s.valid_time)}>{stepLabel(s.step)}</th>)}</tr>
        </thead>
        <tbody>
          {order.map(({ p, li, fl }) => (
            <tr key={p} className={p === currentLevel ? "is-current" : undefined}>
              <th scope="row">FL{String(fl).padStart(3, "0")}</th>
              {m.steps.map((s) => {
                const max = s.awci_max?.[li] ?? null;
                const label = s.missing ? `${stepLabel(s.step)}, FL${fl} : échéance manquante`
                  : max === null ? `${stepLabel(s.step)}, FL${fl} : sous le relief tout le long`
                    : `${stepLabel(s.step)}, FL${fl} : AWCI max ${fmt(max, 0)} (${classLabels[cls(max)] ?? ""}), médiane ${fmt(s.awci_median?.[li] ?? NaN, 0)}, `
                      + `${pct(s.frac_awci_high?.[li])} de la route ≥ High, givrage ${pct(s.frac_icing?.[li])}, `
                      + `CAT ≥ modérée ${pct(s.frac_cat_moderate?.[li])}, nuage ≥ 5/8 ${pct(s.frac_cloud_bkn?.[li])}`;
                const current = s.step === currentStep && p === currentLevel;
                return (
                  <td key={s.step} className={s.missing ? "is-missing" : undefined}>
                    <button type="button" aria-label={label} title={label} aria-pressed={current}
                            disabled={s.missing} onClick={() => onSelect(s.step, p)}
                            style={max !== null && !s.missing ? { background: AWCI_CLASS_COLORS[cls(max)], color: TEXT_ON_CLASS[cls(max)] } : undefined}>
                      {max !== null && !s.missing ? fmt(max, 0) : ""}
                    </button>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
