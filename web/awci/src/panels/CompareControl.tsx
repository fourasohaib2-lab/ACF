import { utcLabel } from "../lib/format";

/** Opacity of the forecast field on the map outside the observation comparison. */
export const FIELD_OPACITY = 0.85;
/** The fade is a comparison tool: it never leaks into other layers or views. */
export const fieldOpacity = (comparing: boolean, fade: number) => (comparing ? fade : FIELD_OPACITY);

interface Props { forecastValid: string | undefined; observedAt: string | undefined; opacity: number; onOpacity: (v: number) => void }

/** Model/observation fade: forecast OLR top temperature over the observed IR 10.5 µm, both times side by side. */
export function CompareControl({ forecastValid, observedAt, opacity, onOpacity }: Props) {
  const gapH = forecastValid && observedAt ? Math.abs(new Date(forecastValid).getTime() - new Date(observedAt).getTime()) / 3_600_000 : null;
  return (
    <div className="compare-control panel">
      <label className="field">
        <span>Fondu prévision ↔ observation</span>
        <input type="range" min={0} max={100} value={Math.round(opacity * 100)} onChange={(e) => onOpacity(Number(e.target.value) / 100)}
               aria-valuetext={`Prévision ${Math.round(opacity * 100)} %`} />
      </label>
      <p className="panel-note">
        Prévision T sommets (OLR) valide {forecastValid ? utcLabel(forecastValid) : "—"} · Observation MTG IR 10,5 µm {observedAt ? utcLabel(observedAt) : "—"}
        {gapH !== null && gapH >= 1 ? ` · écart de ${gapH.toFixed(0)} h entre les deux instants` : ""}
      </p>
    </div>
  );
}
