import type { ProfilePayload } from "../api/types";
import { flLabel, fmt } from "../lib/format";
import { AWCI_CLASS_COLORS } from "../theme/palette";

interface Props { profile: ProfilePayload; awciBounds: number[]; current: number }

/** AWCI per pressure level at the point, highest level on top; below-ground levels are named, not zero. */
export function AwciProfile({ profile, awciBounds, current }: Props) {
  const levels = [...profile.levels].sort((a, b) => a.level_hpa - b.level_hpa);
  return (
    <section className="panel" aria-label="Profil vertical AWCI">
      <h2>Profil vertical AWCI</h2>
      <ul className="bars profile-bars">
        {levels.map((l) => {
          const below = l.awci === null && l.level_layers.gh === null;
          const color = l.awci === null ? undefined : AWCI_CLASS_COLORS[awciBounds.filter((b) => l.awci! >= b).length];
          return (
            <li key={l.level_hpa} aria-current={l.level_hpa === current ? "true" : undefined}>
              <span className="bar-label num">{flLabel(l.flight_level)} · {l.level_hpa}</span>
              {below ? <span className="bar-track bar-below">sous le relief</span> : (
                <span className="bar-track bar-track-dark"><span className="bar-fill" style={{ width: `${l.awci ?? 0}%`, background: color }} /></span>
              )}
              <span className="num">{below ? "" : `${fmt(l.awci, 0)} ${l.awci_level ?? ""}`}</span>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
