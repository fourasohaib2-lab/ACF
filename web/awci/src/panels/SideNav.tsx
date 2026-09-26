import { BookOpen, ClipboardCheck, Cloud, Layers, Map as MapIcon } from "lucide-react";
import type { ReactNode, RefObject } from "react";
import { GROUP_LABELS, type Group, type LayerDef } from "../map/layers";

interface Props {
  layers: LayerDef[];
  layer: string;
  onLayer: (id: string) => void;
  streamlines: boolean;
  onStreamlines: (on: boolean) => void;
  panel: string | undefined;
  onPanel: (panel: string | undefined) => void;
  layerListRef: RefObject<HTMLFieldSetElement | null>;
  children?: ReactNode;
}

const GROUPS: Group[] = ["awci", "hazards", "clouds", "surface", "ensemble", "compare"];

/** Layer choice (only layers present in this run) and sections that exist; later sub-projects add their own. */
export function SideNav({ layers, layer, onLayer, streamlines, onStreamlines, panel, onPanel, layerListRef, children }: Props) {
  return (
    <nav className="sidenav" aria-label="Navigation">
      <ul className="sidenav-sections">
        <li><button type="button" aria-current={!panel ? "page" : undefined} onClick={() => onPanel(undefined)}><MapIcon size={16} aria-hidden="true" />Carte</button></li>
        <li><button type="button" aria-current={panel === "clouds" ? "page" : undefined} onClick={() => onPanel("clouds")}><Cloud size={16} aria-hidden="true" />Nuages</button></li>
        <li><button type="button" aria-current={panel === "validation" ? "page" : undefined} onClick={() => onPanel("validation")}><ClipboardCheck size={16} aria-hidden="true" />Validation</button></li>
        <li><button type="button" aria-current={panel === "api" ? "page" : undefined} onClick={() => onPanel("api")}><BookOpen size={16} aria-hidden="true" />API et registre</button></li>
      </ul>
      <fieldset className="layer-list" ref={layerListRef} tabIndex={-1}>
        <legend><Layers size={16} aria-hidden="true" />Couches <kbd>L</kbd></legend>
        {GROUPS.map((g) => {
          const items = layers.filter((d) => d.group === g);
          if (!items.length) return null;
          return (
            <div key={g} className="layer-group">
              <p className="layer-group-title">{GROUP_LABELS[g]}</p>
              {items.map((d) => (
                <label key={d.id} className="layer-option">
                  <input type="radio" name="layer" value={d.id} checked={d.id === layer} onChange={() => onLayer(d.id)} />
                  <span>{d.label}</span>
                  {d.perLevel && <span className="tag" title="Champ par niveau de pression">niveau</span>}
                </label>
              ))}
            </div>
          );
        })}
        <label className="layer-option layer-extra">
          <input type="checkbox" checked={streamlines} onChange={(e) => onStreamlines(e.target.checked)} />
          <span>Lignes de courant (vent au niveau)</span>
        </label>
      </fieldset>
      {children}
    </nav>
  );
}
