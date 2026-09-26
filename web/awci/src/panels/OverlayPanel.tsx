import { RotateCw, Satellite } from "lucide-react";
import type { WmsLayer } from "../api/types";
import { fr } from "../i18n/fr";

export interface OverlayState { time?: string; error?: boolean; loading?: boolean }
interface Props {
  layers: WmsLayer[] | undefined;
  active: string[];
  states: Record<string, OverlayState>;
  onToggle: (layer: string) => void;
  onRetry: (layer: string) => void;
}
const GROUPS: Record<string, string> = { satellite: "Satellite", clouds: "Produits nuageux", convection: "Convection et foudre", ash: "Cendres volcaniques" };

/** EUMETView observations relayed by the server; an unavailable overlay is disabled, the forecast stays usable. */
export function OverlayPanel({ layers, active, states, onToggle, onRetry }: Props) {
  if (!layers) return null;
  return (
    <fieldset className="layer-list overlay-list">
      <legend><Satellite size={16} aria-hidden="true" />Observations (EUMETSAT)</legend>
      {Object.entries(GROUPS).map(([g, title]) => {
        const items = layers.filter((l) => l.group === g);
        if (!items.length) return null;
        return (
          <div key={g} className="layer-group">
            <p className="layer-group-title">{title}</p>
            {items.map((l) => {
              const s = states[l.layer];
              const failed = !!s?.error;
              return (
                <div key={l.layer}>
                  <label className="layer-option">
                    <input type="checkbox" checked={active.includes(l.layer) && !failed} onChange={() => onToggle(l.layer)} />
                    <span>{l.label}</span>
                  </label>
                  {failed && (
                    <p className="overlay-error" role="alert">{fr.eumetviewDown}
                      <button type="button" className="text-button" onClick={() => onRetry(l.layer)}><RotateCw size={12} aria-hidden="true" />Réessayer</button>
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        );
      })}
    </fieldset>
  );
}
