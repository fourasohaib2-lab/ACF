import { fmt } from "../lib/format";
import { AWCI_CLASS_COLORS, AWCI_CLASS_VIGILANCE, DIVERGING_IFS_GFS, SEQ_BLUE } from "../theme/palette";
import { CATEGORY_COLORS, HAZARDS } from "../lib/aero";
import { GENUS_FAMILY, type LayerDef } from "./layers";

interface Props { def: LayerDef; classLabels: string[]; awciBounds: number[] }

const Swatch = ({ color, hatch = false }: { color?: string; hatch?: boolean }) => (
  <span className={`legend-swatch${hatch ? " legend-hatch" : ""}`} style={color ? { background: color } : undefined} aria-hidden="true" />
);

function Rows({ def, classLabels, awciBounds }: Props) {
  const r = def.render;
  if (r.kind === "awci") {
    return (
      <>
        {AWCI_CLASS_COLORS.map((c, i) => {
          const lo = i === 0 ? 0 : awciBounds[i - 1];
          const hi = awciBounds[i];
          return (
            <li key={c}><Swatch color={c} />{classLabels[i] ?? `Classe ${i}`}
              <span className="legend-vigilance">{AWCI_CLASS_VIGILANCE[i]}</span>
              <span className="legend-range num">{hi === undefined ? `≥ ${lo}` : `${lo}–${hi}`}</span></li>
          );
        })}
      </>
    );
  }
  if (r.kind === "codes") {
    return <>{r.labels.map((label, i) => <li key={label}>{r.colors[i] ? <Swatch color={r.colors[i]!} /> : <Swatch />}
      {label}{r.colors[i] ? "" : " (transparent)"}</li>)}</>;
  }
  if (r.kind === "genus") {
    return <>{GENUS_FAMILY.map((f) => <li key={f.label}><Swatch color={f.color} />{f.label}</li>)}
      <li><Swatch />Ciel clair (transparent)</li></>;
  }
  if (r.kind === "diverging") {
    return (
      <li className="legend-ramp">
        <span className="legend-gradient" style={{ background: `linear-gradient(to right, ${DIVERGING_IFS_GFS.join(",")})` }} aria-hidden="true" />
        <span className="legend-ends num"><span>≤ −{r.limit} (GFS plus bas)</span><span>0</span><span>≥ +{r.limit} (GFS plus haut)</span></span>
      </li>
    );
  }
  const scale = r.scale ?? 1;
  const [lo, hi] = r.invert ? [r.max, r.min] : [r.min, r.max];
  // openEnd: the ramp saturates at its maximum, which then reads "≥ max" (e.g. ceilings above 10 000 ft)
  const end = (v: number) => `${r.openEnd && v === r.max ? "≥ " : ""}${show(v)}`;
  const show = (v: number) => (def.id === "cloud_top_teff_k" ? fmt(v - 273.15, 0) : fmt(v * scale, scale === 1 ? 1 : 0));
  return (
    <li className="legend-ramp">
      <span className="legend-gradient" style={{ background: `linear-gradient(to right, ${SEQ_BLUE.join(",")})` }} aria-hidden="true" />
      <span className="legend-ends num"><span>{end(lo)}</span><span>{`${end(hi)} ${def.unit}`}</span></span>
    </li>
  );
}

/** Observation legend, one line under the map (it must never cover the forecast field). */
export function ObsLegend({ metar, hazards }: { metar: boolean; hazards: string[] }) {
  if (!metar && !hazards.length) return null;
  return (
    <ul className="obs-legend" aria-label="Légende des observations">
      {metar && (
        <li className="legend-aero">
          <span>Aérodromes, catégorie FAA (METAR ± 30 min) :</span>
          {(Object.keys(CATEGORY_COLORS) as (keyof typeof CATEGORY_COLORS)[]).map((c) => (
            <span key={c} className="legend-chip"><span className="legend-dot" style={{ background: CATEGORY_COLORS[c] }} aria-hidden="true" />{c}</span>
          ))}
          <span className="legend-chip"><span className="legend-dot legend-dot-empty" aria-hidden="true" />sans obs.</span>
          <span className="legend-chip"><span className="legend-dot legend-dot-ring" aria-hidden="true" />TCU/CB observé</span>
        </li>
      )}
      {hazards.map((h) => {
        const style = HAZARDS[h as keyof typeof HAZARDS];
        return style ? <li key={h}><Swatch color={style.color} />SIGMET {style.label}</li> : null;
      })}
    </ul>
  );
}

/** Layers drawn with the ONM vigilance colours (AWCI classes, CAT, icing, convection). */
export const usesVigilance = (def: LayerDef) =>
  !def.source && (def.render.kind === "awci" || ["cat_category", "icing_potential", "convective_class"].includes(def.id));

export function Legend(props: Props) {
  return (
    <figure className="legend" aria-label={`Légende : ${props.def.label}`}>
      <figcaption>{props.def.label}{props.def.unit && props.def.render.kind === "continuous" ? "" : props.def.unit ? ` (${props.def.unit})` : ""}</figcaption>
      <ul>
        <Rows {...props} />
        {props.def.nanMeaning
          ? <li><Swatch />{props.def.nanMeaning} (transparent)</li>
          : <li><Swatch hatch />Sans donnée, sous le relief ou indéterminé</li>}
      </ul>
      {usesVigilance(props.def) && <p className="legend-note" title="Couleurs de la convention de vigilance ONM (vert, jaune, orange, rouge), sans valeur de vigilance officielle : AWCI n'est pas un produit de vigilance.">Teintes vigilance ONM, non officielles</p>}
    </figure>
  );
}
