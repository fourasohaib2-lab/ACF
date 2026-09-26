/**
 * ONM vigilance convention (BMS levels: green, yellow I, orange II, red III), applied to the AWCI classes and to the
 * hazard categories. These colours carry no official vigilance: AWCI is not an ONM warning product. The ONM
 * publishes no hex codes: the shades were chosen by measurement (2026-09-26, tools/awci/check_palette.py,
 * docs/awci/AWCI_WEB_COLORS.md):
 * - contrast on the map surface #0b1220 >= 3:1 for every class (WCAG 1.4.11): 3.65, 7.92, 15.3, 8.29, 4.68, 3.27;
 * - smallest CIEDE2000 difference between any two classes, Machado et al. (2009) simulations at full severity:
 *   normal 20.7, deuteranopia 10.2, protanopia 6.3 (dark green / red, non-adjacent), tritanopia 13.8.
 */
export const VIGILANCE = { green: "#66bb6a", yellow: "#ffeb3b", orange: "#ff9100", red: "#e8413c" } as const;
/** AWCI classes Very Low … Extreme: two greens, yellow, orange, red, and crimson purple beyond red for Extreme. */
export const AWCI_CLASS_COLORS = ["#2e7d32", VIGILANCE.green, VIGILANCE.yellow, VIGILANCE.orange, VIGILANCE.red, "#a52cba"] as const;
/** Vigilance level of each AWCI class, for the legend. */
export const AWCI_CLASS_VIGILANCE = ["vert", "vert", "jaune", "orange", "rouge", "rouge (au-delà)"] as const;
/** Text on an AWCI class colour, WCAG AA >= 4.5:1 measured: 5.13, 7.92, 15.3, 8.29, 4.68, 5.72. */
export const TEXT_ON_AWCI_CLASS = ["#ffffff", "#0b1220", "#0b1220", "#0b1220", "#0b1220", "#ffffff"] as const;
/** dataviz reference sequential blue, darkest -> lightest (low values recede into the dark surface). */
export const SEQ_BLUE = ["#0d366b", "#104281", "#184f95", "#1c5cab", "#256abf", "#2a78d6", "#3987e5", "#5598e7",
  "#6da7ec", "#86b6ef", "#9ec5f4", "#b7d3f6", "#cde2fb"] as const;
/** dataviz dark categorical slots 1-3: the only ones valid for all pairs (maps). */
export const CATEGORICAL = ["#3987e5", "#d95926", "#199e70"] as const;
export const STATUS = { ok: "#0ca30c", attention: "#fab219", serious: "#ec835a", critical: "#d03b3b" } as const;
export type Rgb = [number, number, number];
export const HATCH: [number, number, number, number] = [137, 135, 129, 150];

export function hexToRgb(hex: string): Rgb {
  const n = Number.parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

export function rampColor(stops: readonly string[], t: number): Rgb {
  const x = Math.min(1, Math.max(0, t)) * (stops.length - 1);
  const i = Math.min(stops.length - 2, Math.floor(x));
  const a = hexToRgb(stops[i]!);
  const b = hexToRgb(stops[i + 1]!);
  const f = x - i;
  return [0, 1, 2].map((k) => Math.round(a[k]! + (b[k]! - a[k]!) * f)) as Rgb;
}

/** Chart series colours resolved per theme by CSS (dark or light categorical slots 1-3, both validated). */
export const SERIES = ["var(--series-1)", "var(--series-2)", "var(--series-3)"] as const;
