// Static simulated datasets for the AWCI reference dashboard.

export const KPIS = [
  { label: "GLOBAL MEAN AWCI", value: "38.4", unit: "idx", trend: "+2.1", tone: "normal" as const },
  { label: "MAX AWCI", value: "92", unit: "idx", trend: "+7", tone: "critical" as const },
  { label: "AFFECTED AREA", value: "1.24", unit: "M km²", trend: "+0.3", tone: "warning" as const },
  { label: "FORECAST CONFIDENCE", value: "87", unit: "%", trend: "-1.4", tone: "normal" as const },
]

// Vertical cross-section: complexity vs flight level
export const CROSS_SECTION = Array.from({ length: 24 }, (_, i) => {
  const fl = 100 + i * 20 // FL100 -> FL560
  const base = Math.sin((i / 23) * Math.PI * 1.4) * 40 + 45
  const noise = Math.cos(i * 1.7) * 8
  return {
    fl: `FL${fl}`,
    flNum: fl,
    complexity: Math.max(4, Math.round(base + noise)),
  }
})

export const RADAR = [
  { axis: "Thermodynamic", value: 78, ref: 55 },
  { axis: "Convective", value: 91, ref: 60 },
  { axis: "Turbulence", value: 64, ref: 48 },
  { axis: "Icing", value: 52, ref: 40 },
  { axis: "Wind Shear", value: 73, ref: 50 },
  { axis: "Visibility", value: 38, ref: 45 },
]

export const RADAR_TABLE = [
  { name: "Thermodynamic", value: 78, delta: "+12" },
  { name: "Convective", value: 91, delta: "+23" },
  { name: "Turbulence", value: 64, delta: "+8" },
  { name: "Icing", value: 52, delta: "+3" },
  { name: "Wind Shear", value: 73, delta: "+15" },
  { name: "Visibility", value: 38, delta: "-6" },
]

// Route elevation / flight profile
export const ROUTE_PROFILE = Array.from({ length: 40 }, (_, i) => {
  const x = i / 39
  const cruise = 380
  let alt: number
  if (x < 0.12) alt = (x / 0.12) * cruise
  else if (x > 0.86) alt = ((1 - x) / 0.14) * cruise
  else alt = cruise + Math.sin(x * 10) * 8
  const risk = Math.max(0, Math.sin(x * 7 + 1) * 45 + 40 + Math.cos(x * 13) * 12)
  return {
    dist: Math.round(x * 3200),
    alt: Math.round(Math.max(0, alt)),
    risk: Math.round(risk),
  }
})

export const RISK_SUMMARY = [
  { label: "Turbulence", level: "SEVERE", value: 82, tone: "critical" as const },
  { label: "Icing", level: "MODERATE", value: 54, tone: "warning" as const },
  { label: "Convective", level: "HIGH", value: 91, tone: "critical" as const },
  { label: "Wind Shear", level: "MODERATE", value: 61, tone: "warning" as const },
]

export const RECOMMENDATIONS = [
  "Deviate 40NM north of WPT DINIM to avoid convective cell cluster.",
  "Request FL360 climb after MADOT to clear moderate icing layer.",
  "Expect sustained CAT between BEDRA and NATEB — secure cabin.",
]

// Floating hover-point readout over the map
export const HOVER_POINT = {
  lat: "48.24° N",
  lon: "011.36° E",
  fl: "FL300",
  awci: 92,
  cloudTop: "FL410",
  echoTop: "FL440",
  cape: "2140 J/kg",
  shear: "34 kt",
}

export const MAP_LAYERS = [
  { id: "awci", label: "AWCI Composite", active: true },
  { id: "convective", label: "Convective", active: true },
  { id: "thermo", label: "Thermodynamic", active: false },
  { id: "wind", label: "Wind Vectors", active: false },
  { id: "routes", label: "ATS Routes", active: true },
]

export const TIMELINE = [
  "00:00Z", "03:00Z", "06:00Z", "09:00Z", "12:00Z", "15:00Z", "18:00Z", "21:00Z", "24:00Z",
]
