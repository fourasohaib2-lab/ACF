import { Plane } from "lucide-react";
import type { AirportsPayload } from "../api/types";
import { ageLabel } from "../lib/format";
import type { AeroLayer } from "../state/view";

interface Props {
  airports: AirportsPayload | undefined;
  layers: AeroLayer[];
  selected: string | undefined;
  now: Date;
  onLayers: (layers: AeroLayer[]) => void;
  onSelect: (icao: string | undefined) => void;
}

/** Aeronautical observation layers and a keyboard-operable aerodrome chooser (the map canvas is not). */
export function AeroControls({ airports, layers, selected, now, onLayers, onSelect }: Props) {
  const toggle = (l: AeroLayer) => onLayers(layers.includes(l) ? layers.filter((x) => x !== l) : [...layers, l]);
  const sorted = [...(airports?.airports ?? [])].sort((a, b) => a.icao.localeCompare(b.icao));
  return (
    <fieldset className="layer-list aero-controls">
      <legend><Plane size={16} aria-hidden="true" />Observations aéronautiques</legend>
      <label className="layer-option">
        <input type="checkbox" checked={layers.includes("metar")} onChange={() => toggle("metar")} />
        <span>Aérodromes (METAR à ± 30 min)</span>
      </label>
      <label className="layer-option">
        <input type="checkbox" checked={layers.includes("sigmet")} onChange={() => toggle("sigmet")} />
        <span>SIGMET (dont cendres volcaniques)</span>
      </label>
      <label className="field aero-select">
        <span>Aérodrome</span>
        <select value={selected ?? ""} onChange={(e) => onSelect(e.target.value || undefined)} disabled={!sorted.length}>
          <option value="">{sorted.length ? "Choisir…" : "Aucun aérodrome"}</option>
          {sorted.map((a) => <option key={a.icao} value={a.icao}>{a.icao} — {a.name}</option>)}
        </select>
      </label>
      <p className="panel-note">
        {airports?.ingested_at ? `AWC, ingéré ${ageLabel(airports.ingested_at, now)}` : "Aucune observation ingérée : lancer acf-awci-obs."}
      </p>
    </fieldset>
  );
}
