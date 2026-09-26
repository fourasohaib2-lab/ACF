import { Box, Map as MapIcon } from "lucide-react";
import { allowedWith, VOLUME_LAYERS, type VolumeLayerId } from "./layers3d";

export type CameraPreset = "top" | "south" | "west";
const OKTA_NAMES: Record<number, string> = { 1: "FEW", 2: "FEW", 3: "SCT", 4: "SCT", 5: "BKN", 6: "BKN", 7: "BKN", 8: "OVC" };

interface Props {
  vol: VolumeLayerId[];
  exag: number;
  cth: number;
  loading: boolean;
  onChange: (patch: { vol?: VolumeLayerId[]; exag?: number; cth?: number }) => void;
  onCamera: (preset: CameraPreset) => void;
  onExit: () => void;
}

/** Controls of the 3-D view (spec SP2B §2): at most two layers, exaggeration always stated, legend of what is drawn. */
export function View3DControls({ vol, exag, cth, loading, onChange, onCamera, onExit }: Props) {
  const toggle = (id: VolumeLayerId) => onChange({ vol: vol.includes(id) ? vol.filter((x) => x !== id) : [...vol, id] });
  const oktas = Math.round(cth * 8);
  return (
    <section className="panel view3d-controls" aria-label="Vue 3D">
      <div className="view3d-head">
        <h2><Box size={16} aria-hidden="true" /> Vue volume 3D</h2>
        <button type="button" className="text-button" onClick={onExit}><MapIcon size={14} aria-hidden="true" />Revenir en 2D</button>
      </div>
      <p className="notice">Relief et altitudes exagérés ×{exag}. Voxels = mailles IFS 0,25° réelles, entre interfaces de niveaux ; rien n'est interpolé.</p>
      {loading && <p className="panel-note" role="status">Chargement du volume…</p>}
      <fieldset className="layer-list">
        <legend>Couches volumiques (2 au plus)</legend>
        {VOLUME_LAYERS.map((d) => (
          <label key={d.id} className="layer-option">
            <input type="checkbox" checked={vol.includes(d.id)} disabled={!vol.includes(d.id) && !allowedWith(vol, d.id)}
                   onChange={() => toggle(d.id)} />
            <span>{d.label}</span>
          </label>
        ))}
      </fieldset>
      <label className="field">
        <span>Seuil de fraction nuageuse : {oktas}/8 ({OKTA_NAMES[oktas]})</span>
        <input type="range" min={1} max={8} step={1} value={oktas} aria-valuetext={`${oktas}/8 (${OKTA_NAMES[oktas]})`}
               aria-label="Seuil de fraction nuageuse" onChange={(e) => onChange({ cth: Number(e.target.value) / 8 })} />
      </label>
      <label className="field">
        <span>Exagération verticale ×{exag}</span>
        <input type="range" min={10} max={100} step={10} value={exag} aria-label="Exagération verticale"
               onChange={(e) => onChange({ exag: Number(e.target.value) })} />
      </label>
      <div className="view3d-camera" role="group" aria-label="Caméra">
        <button type="button" className="text-button" onClick={() => onCamera("top")}>Vue de dessus</button>
        <button type="button" className="text-button" onClick={() => onCamera("south")}>Oblique sud</button>
        <button type="button" className="text-button" onClick={() => onCamera("west")}>Oblique ouest</button>
      </div>
      <ul className="obs-legend" aria-label="Légende 3D">
        {VOLUME_LAYERS.filter((d) => vol.includes(d.id)).flatMap((d) => d.legend.map((row) => (
          <li key={`${d.id}-${row.label}`}><span className="legend-swatch" style={{ background: row.color }} aria-hidden="true" />{row.label}</li>
        )))}
        <li><span className="legend-swatch" style={{ background: "#6d7a95" }} aria-hidden="true" />Relief (surface du modèle IFS)</li>
      </ul>
      <p className="panel-note">{VOLUME_LAYERS.filter((d) => vol.includes(d.id)).map((d) => d.note).join(" ")} Clic sur un voxel : inspecteur au point et au niveau.
        Maj + flèches (carte active) : rotation et inclinaison.</p>
    </section>
  );
}
