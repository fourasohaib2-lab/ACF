/**
 * Volume layers of the 3-D view (spec SP2B §2). Each selects hazardous or cloudy cells only, so the scene
 * stays readable; colours are chosen so that any two layers allowed together never share a hue.
 */
import { AWCI_CLASS_COLORS, CATEGORICAL, STATUS, hexToRgb } from "../theme/palette";
import type { Rgba } from "./geometry";

export type VolumeLayerId = "clouds" | "icing" | "cat" | "awci";
export interface VolumeLayerDef {
  id: VolumeLayerId;
  label: string;
  source: string; // /volume layer
  aux?: string; // second /volume layer the classifier reads (clouds: genus)
  palette: Rgba[];
  legend: { label: string; color: string }[];
  note: string;
}
export interface ClassifyParams { threshold: number; awciBounds: number[]; aux: Float32Array | undefined }

/** Opacity bins of cloud cover above the threshold (more cover, more opaque). */
export const CLOUD_BINS = 3;
const ALPHA = [110, 160, 215];
const rgba = (hex: string, a: number): Rgba => [...hexToRgb(hex), a];

// Genus families (WMO 0500 codes): 0-7 stratiform and sheet clouds, 8 Cu (incl. TCU), 9 Cb.
const FAMILIES = [
  { label: "Stratiformes et en nappes (Ci … St)", color: "#c9d3e3" },
  { label: "Cumulus, TCU", color: CATEGORICAL[2] },
  { label: "Cumulonimbus", color: CATEGORICAL[1] },
] as const;
const family = (code: number) => (code === 9 ? 2 : code === 8 ? 1 : code >= 0 && code <= 7 ? 0 : -1);

export const VOLUME_LAYERS: VolumeLayerDef[] = [
  { id: "clouds", label: "Nuages par genre", source: "cloud_fraction", aux: "cloud_genus",
    palette: FAMILIES.flatMap((f) => ALPHA.map((a) => rgba(f.color, a))),
    legend: FAMILIES.map((f) => ({ label: f.label, color: f.color })),
    note: "Fraction nuageuse au niveau ≥ seuil (Sundqvist, HYPOTHESIS) ; opacité croissante avec la couverture." },
  { id: "icing", label: "Givrage potentiel", source: "icing_potential", palette: [rgba(CATEGORICAL[0], 170)],
    legend: [{ label: "Givrage potentiel (0 à −20 °C, air saturé)", color: CATEGORICAL[0] }],
    note: "Niveaux où le givrage potentiel vaut 1 (SP1)." },
  { id: "cat", label: "Turbulence en air clair", source: "cat_category",
    palette: [rgba(STATUS.attention, 150), rgba(STATUS.serious, 200)],
    legend: [{ label: "Modérée", color: STATUS.attention }, { label: "Modérée à sévère", color: STATUS.serious }],
    note: "Indice d'Ellrod TI2, catégorie ≥ modérée." },
  { id: "awci", label: "AWCI ≥ High", source: "awci",
    palette: AWCI_CLASS_COLORS.slice(3).map((c) => rgba(c, 190)),
    legend: [{ label: "High", color: AWCI_CLASS_COLORS[3] }, { label: "Very High", color: AWCI_CLASS_COLORS[4] },
      { label: "Extreme", color: AWCI_CLASS_COLORS[5] }],
    note: "Classes AWCI High, Very High et Extreme (bornes du profil)." },
];

export function classifier(def: VolumeLayerDef, p: ClassifyParams): (value: number, level: number, index: number) => number {
  switch (def.id) {
    case "clouds":
      return (v, _k, i) => {
        if (v < p.threshold) return -1;
        const f = family(p.aux ? p.aux[i]! : -1);
        if (f < 0) return -1;
        const bin = Math.min(CLOUD_BINS - 1, Math.floor(((v - p.threshold) / Math.max(1e-6, 1 - p.threshold)) * CLOUD_BINS));
        return f * CLOUD_BINS + bin;
      };
    case "icing":
      return (v) => (v >= 1 ? 0 : -1);
    case "cat":
      return (v) => (v >= 3 ? 1 : v >= 2 ? 0 : -1);
    case "awci":
      return (v) => {
        const cls = p.awciBounds.filter((b) => v >= b).length;
        return cls >= 3 ? Math.min(2, cls - 3) : -1;
      };
  }
}

/** At most two layers at once; AWCI and CAT are exclusive. */
export function allowedWith(active: VolumeLayerId[], candidate: VolumeLayerId): boolean {
  if (active.includes(candidate)) return true;
  if (active.length >= 2) return false;
  const pair = new Set([...active, candidate]);
  return !(pair.has("awci") && pair.has("cat"));
}
