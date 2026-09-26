import type { SigmetCollection } from "../api/types";
import { flText, HAZARDS } from "../lib/aero";
import { utcLabel } from "../lib/format";

interface Props { sigmets: SigmetCollection | undefined; isError: boolean }

/** International SIGMETs valid at the time on screen, crossing the domain (text first, colour second). */
export function SigmetList({ sigmets, isError }: Props) {
  const items = sigmets?.features ?? [];
  return (
    <section className="panel sigmet-list" aria-label="SIGMET">
      <h2>SIGMET {sigmets ? `valides à ${utcLabel(sigmets.time)}` : ""}</h2>
      {isError && <p className="notice">SIGMET indisponibles (archive des observations illisible).</p>}
      {sigmets && !items.length && <p className="panel-note">Aucun SIGMET valide à cette heure sur le domaine.</p>}
      <ul>
        {items.map((f) => {
          const p = f.properties;
          const h = HAZARDS[p.hazard];
          return (
            <li key={p.raw} className={`sigmet-item${p.hazard === "VA" ? " is-ash" : ""}`}>
              <p className="sigmet-head">
                <span className="legend-swatch" style={{ background: h.color }} aria-hidden="true" />
                <strong>{h.label}</strong>{p.qualifier ? ` · ${p.qualifier}` : ""}
                <span className="num"> {flText(p.base_ft)}–{flText(p.top_ft)}</span>
              </p>
              <p className="panel-note">
                {p.fir_name ?? p.fir ?? ""} · valide {utcLabel(p.valid_from)} → {utcLabel(p.valid_to)}
                {p.direction ? ` · se déplace vers ${p.direction}${p.speed_kt ? ` à ${Number(p.speed_kt)} kt` : ""}` : ""}
              </p>
              <details><summary>Texte du SIGMET</summary><pre className="mono raw-text">{p.raw}</pre></details>
            </li>
          );
        })}
      </ul>
      <p className="provenance">{sigmets?.attribution ?? "Aviation Weather Center, NOAA/NWS"}</p>
    </section>
  );
}
