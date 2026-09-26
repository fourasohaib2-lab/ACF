import type { CloudsSeries } from "../api/types";
import { stepLabel } from "../lib/format";
import { CATEGORICAL } from "../theme/palette";

const SHORT: Record<string, string> = {
  Ci: "Ci", Cc: "Cc", Cs: "Cs", Ac: "Ac", As: "As", Ns: "Ns", Sc: "Sc", St: "St", Cu: "Cu", Cb: "Cb", clear: "·", indeterminate: "?",
};
export const familyColor = (g: string | null | undefined) =>
  g === "Cb" ? CATEGORICAL[1] : g === "Cu" ? CATEGORICAL[2] : g && g !== "clear" && g !== "indeterminate" ? CATEGORICAL[0] : undefined;

/** Temporal variability of the diagnosis: probable genus per etage and step, abbreviation always written. */
export function GenusTimeline({ series, currentStep }: { series: CloudsSeries; currentStep: number }) {
  const rows: { key: "high" | "mid" | "low"; label: string }[] = [
    { key: "high", label: "Haut" }, { key: "mid", label: "Moyen" }, { key: "low", label: "Bas" },
  ];
  return (
    <table className="genus-timeline" aria-label="Genre probable par étage et par échéance">
      <thead><tr><th scope="col">Étage</th>{series.points.map((p) => <th key={p.step} scope="col"
        aria-current={p.step === currentStep ? "true" : undefined}>{stepLabel(p.step)}</th>)}</tr></thead>
      <tbody>
        {rows.map((r) => (
          <tr key={r.key}>
            <th scope="row">{r.label}</th>
            {series.points.map((p) => {
              const g = p.missing ? null : p.genus?.[r.key] ?? null;
              const color = familyColor(g);
              return (
                <td key={p.step} className={p.missing ? "missing" : ""} aria-current={p.step === currentStep ? "true" : undefined}
                    style={color ? { background: color } : undefined} title={p.missing ? "échéance manquante" : g ?? "—"}>
                  {p.missing ? "∅" : SHORT[g ?? ""] ?? "—"}
                </td>
              );
            })}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
