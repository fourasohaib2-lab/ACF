import { Pause, Play } from "lucide-react";
import type { Meta } from "../api/types";
import { fr } from "../i18n/fr";
import { stepLabel, utcLabel } from "../lib/format";

interface Props {
  meta: Meta;
  step: number;
  onStep: (step: number) => void;
  playing?: boolean;
  onTogglePlay?: () => void;
}

/** Forecast steps of the run: missing steps are shown, disabled and announced, never replaced by a neighbour. */
export function TimeBar({ meta, step, onStep, playing = false, onTogglePlay }: Props) {
  const current = meta.steps.indexOf(step);
  return (
    <div className="timebar" role="group" aria-label="Échéances de prévision">
      {onTogglePlay && (
        <button type="button" className="icon-button" onClick={onTogglePlay}
                aria-label={playing ? "Arrêter la lecture" : "Lire les échéances (1 par seconde)"} aria-pressed={playing}>
          {playing ? <Pause size={16} aria-hidden="true" /> : <Play size={16} aria-hidden="true" />}
        </button>
      )}
      <ol className="timebar-steps">
        {meta.steps.map((s, i) => {
          const missing = meta.missing_steps.includes(s);
          const valid = meta.valid_times[i] ?? "";
          return (
            <li key={s}>
              <button type="button" className="timebar-step" disabled={missing} aria-current={i === current ? "step" : undefined}
                      aria-label={`${stepLabel(s)}, ${missing ? fr.missingStep : `valide ${utcLabel(valid)}`}`}
                      title={missing ? fr.missingStep : utcLabel(valid)} onClick={() => onStep(s)}>
                <span className="num">{stepLabel(s)}</span>
              </button>
            </li>
          );
        })}
      </ol>
      <span className="timebar-valid num" aria-live="polite">{current >= 0 ? `Valide ${utcLabel(meta.valid_times[current]!)}` : ""}</span>
    </div>
  );
}
