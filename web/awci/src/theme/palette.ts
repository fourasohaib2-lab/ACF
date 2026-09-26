/** AWCI ordinal classes, dark theme, validated with dataviz validate_palette --ordinal --mode dark --surface #0b1220. */
export const AWCI_CLASS_COLORS = ["#854494", "#b94c90", "#e45d84", "#ff7f6c", "#ffa85d", "#ffd368"] as const;
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
