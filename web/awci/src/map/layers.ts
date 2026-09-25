import { AWCI_CLASS_COLORS, CATEGORICAL, SEQ_BLUE, hexToRgb, rampColor } from "../theme/palette";

export type Rgba = [number, number, number, number];
export type Group = "awci" | "hazards" | "clouds" | "surface";
export type Render =
  | { kind: "awci" }
  | { kind: "codes"; colors: (string | null)[]; labels: string[] }
  | { kind: "continuous"; min: number; max: number; invert?: boolean; scale?: number; unitLabel?: string }
  | { kind: "genus" };
export interface LayerDef { id: string; label: string; group: Group; perLevel: boolean; unit: string; render: Render }

export const GROUP_LABELS: Record<Group, string> = {
  awci: "AWCI", hazards: "Dangers", clouds: "Nuages", surface: "Surface et précipitations",
};
const S = SEQ_BLUE;
const cont = (min: number, max: number, extra: Partial<Extract<Render, { kind: "continuous" }>> = {}): Render =>
  ({ kind: "continuous", min, max, ...extra });

export const LAYER_DEFS: LayerDef[] = [
  { id: "awci", label: "AWCI", group: "awci", perLevel: true, unit: "0–100", render: { kind: "awci" } },
  { id: "cat_category", label: "Turbulence en air clair", group: "hazards", perLevel: true, unit: "classe",
    render: { kind: "codes", colors: [null, S[6], S[9], S[12]], labels: ["Nulle", "Légère", "Modérée", "Modérée à sévère"] } },
  { id: "icing_potential", label: "Givrage potentiel", group: "hazards", perLevel: true, unit: "oui/non",
    render: { kind: "codes", colors: [null, S[10]], labels: ["Non", "Oui"] } },
  { id: "vertical_shear", label: "Cisaillement vertical", group: "hazards", perLevel: true, unit: "10⁻³ s⁻¹",
    render: cont(0, 0.012, { scale: 1000 }) },
  { id: "wind_speed", label: "Vent", group: "hazards", perLevel: true, unit: "m/s", render: cont(0, 80) },
  { id: "mucape", label: "Instabilité (MUCAPE)", group: "hazards", perLevel: false, unit: "J/kg", render: cont(0, 3000) },
  { id: "convective_class", label: "Convection (Cu, TCU, Cb)", group: "clouds", perLevel: false, unit: "classe",
    render: { kind: "codes", colors: [null, S[5], CATEGORICAL[2], CATEGORICAL[1], CATEGORICAL[1]],
      labels: ["Aucune", "Cu humilis/mediocris", "TCU", "Cb calvus", "Cb capillatus"] } },
  { id: "genus_low", label: "Genre, étage bas", group: "clouds", perLevel: false, unit: "", render: { kind: "genus" } },
  { id: "genus_mid", label: "Genre, étage moyen", group: "clouds", perLevel: false, unit: "", render: { kind: "genus" } },
  { id: "genus_high", label: "Genre, étage haut", group: "clouds", perLevel: false, unit: "", render: { kind: "genus" } },
  { id: "cloud_cover_low", label: "Couverture basse", group: "clouds", perLevel: false, unit: "octas", render: cont(0, 1, { scale: 8 }) },
  { id: "cloud_cover_mid", label: "Couverture moyenne", group: "clouds", perLevel: false, unit: "octas", render: cont(0, 1, { scale: 8 }) },
  { id: "cloud_cover_high", label: "Couverture haute", group: "clouds", perLevel: false, unit: "octas", render: cont(0, 1, { scale: 8 }) },
  { id: "cloud_fraction", label: "Fraction nuageuse au niveau", group: "clouds", perLevel: true, unit: "octas", render: cont(0, 1, { scale: 8 }) },
  { id: "ceiling_m", label: "Plafond (OACI)", group: "clouds", perLevel: false, unit: "ft", render: cont(0, 3048, { invert: true, scale: 1 / 0.3048 }) },
  { id: "cloud_top_teff_k", label: "Température des sommets (OLR)", group: "clouds", perLevel: false, unit: "°C",
    render: cont(200, 300, { invert: true }) },
  { id: "column_condensate", label: "Condensat colonne", group: "clouds", perLevel: false, unit: "kg/m²", render: cont(0, 5) },
  { id: "precip_class", label: "Précipitations (OMM)", group: "surface", perLevel: false, unit: "classe",
    render: { kind: "codes", colors: [null, S[4], S[7], S[10], S[12]], labels: ["Nulles", "Faibles", "Modérées", "Fortes", "Violentes"] } },
  { id: "snowfall_mm", label: "Chute de neige (3 h)", group: "surface", perLevel: false, unit: "mm eau", render: cont(0, 20) },
  { id: "snow_depth_cm", label: "Épaisseur de neige", group: "surface", perLevel: false, unit: "cm", render: cont(0, 100) },
  { id: "freezing_precip_mm", label: "Précipitations verglaçantes (3 h)", group: "surface", perLevel: false, unit: "mm", render: cont(0, 10) },
  { id: "gust_10m", label: "Rafales à 10 m", group: "surface", perLevel: false, unit: "m/s", render: cont(0, 40) },
  { id: "dust_proxy", label: "Soulèvement de poussière (proxy)", group: "surface", perLevel: false, unit: "0–1", render: cont(0, 1) },
];

export function layerDef(id: string): LayerDef {
  const def = LAYER_DEFS.find((d) => d.id === id);
  if (!def) throw new Error(`unknown layer ${id}`);
  return def;
}

/** WMO 0500 codes folded into the three map-valid categorical slots; exact genus in the inspector. */
export const GENUS_FAMILY = [
  { label: "Stratiformes et en nappes (Ci, Cc, Cs, Ac, As, Ns, Sc, St)", color: CATEGORICAL[0] },
  { label: "Cumulus, TCU", color: CATEGORICAL[2] },
  { label: "Cumulonimbus", color: CATEGORICAL[1] },
] as const;

const rgba = (hex: string): Rgba => [...hexToRgb(hex), 255];

export function colorFn(def: LayerDef, awciBounds: number[]): (v: number) => Rgba | null {
  const r = def.render;
  switch (r.kind) {
    case "awci":
      return (v) => rgba(AWCI_CLASS_COLORS[awciBounds.filter((b) => v >= b).length]!);
    case "codes":
      return (v) => { const c = r.colors[Math.round(v)]; return c ? rgba(c) : null; };
    case "genus":
      return (v) => {
        if (v === 9) return rgba(CATEGORICAL[1]);
        if (v === 8) return rgba(CATEGORICAL[2]);
        return v >= 0 && v <= 7 ? rgba(CATEGORICAL[0]) : null;
      };
    case "continuous":
      return (v) => {
        const t = (v - r.min) / (r.max - r.min);
        return [...rampColor(SEQ_BLUE, r.invert ? 1 - t : t), 255];
      };
  }
}
