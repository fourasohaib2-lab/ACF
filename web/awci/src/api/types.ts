/** Types of the /api/v1/awci responses, taken from the real responses served over the fixture cubes. */
export type Num = number | null;

export interface Provenance {
  model: string; run: string; step: number | null; valid_time: string | null; domain: string;
  profile: string; profile_version: string; license: string; attribution: string;
}
export interface Domain {
  name: string; label: string; south: number; north: number; west: number; east: number;
  default: boolean; resolution_deg: number;
}
export interface RunInfo {
  run: string; run_time: string; status: "complete" | "partial" | "failed"; steps: number[];
  missing_steps: number[]; ingested_at: string | null;
}
export interface CloudConsistency { step: number; bias_mean: Num; bias_std: Num; status: string }
export interface Meta {
  levels_hpa: number[]; flight_levels: number[]; steps: number[]; valid_times: string[]; missing_steps: number[];
  status: string; level_layers: string[]; surface_layers: string[];
  cloud_status: "ok" | "degraded" | null; cloud_consistency: CloudConsistency[] | null;
  accumulation_interval_h: (number | null)[] | null; cloud_profile: { name: string; version: string } | null;
  provenance: Provenance;
}
export interface FieldData {
  values: Float32Array; ny: number; nx: number; lat0: number; lat1: number; lon0: number; lon1: number; unit: string;
}
export type Modules = Record<"dynamic" | "thermodynamic" | "convective" | "microphysical" | "topographic", Num>;
export interface LevelPayload {
  awci: Num; awci_level: string | null; modules: Modules; excluded_modules: string[]; missing_inputs: string[];
  present_weight: number; decomposition: Record<string, Num>; level_layers: Record<string, Num>;
  scientific_status: Record<string, string>;
}
export interface PointPayload extends LevelPayload {
  lat: number; lon: number; level_hpa: number; flight_level: number; surface_layers: Record<string, Num>;
  elevation_m: Num; provenance: Provenance;
}
export interface ProfileLevel extends LevelPayload { level_hpa: number; flight_level: number; dewpoint_k: Num }
export interface ProfilePayload { lat: number; lon: number; levels: ProfileLevel[]; provenance: Provenance }
export interface TimeseriesPoint {
  step: number; valid_time: string; awci: Num; modules: Modules; missing_inputs: string[]; present_weight: number;
  decomposition: Record<string, Num>;
}
export interface TimeseriesPayload { lat: number; lon: number; level_hpa: number; points: TimeseriesPoint[] }
export type Badge = "ok" | "attention" | "serious" | "critical" | null;
export interface Summary {
  awci_p95: Num; awci_class: string | null; turbulence_area_pct: Num; convection_area_pct: Num; mucape_max: Num;
  icing_area_pct: Num; shear_p95: Num; heavy_precip_area_pct: Num; low_ceiling_area_pct: Num; cb_area_pct: Num;
  cloud_cover_bias_mean: Num; valid_cells_pct: Num; badges: Record<string, Badge>;
  awci_p95_by_level: { level_hpa: number; flight_level: number; awci_p95: Num }[];
  level_hpa: number; provenance: Provenance;
}
export interface SummaryPoint {
  step: number; valid_time: string; missing: boolean; awci_p95?: Num; turbulence_area_pct?: Num;
  icing_area_pct?: Num; convection_area_pct?: Num; cb_area_pct?: Num;
}
export interface SummarySeries { level_hpa: number; points: SummaryPoint[] }
export interface CloudLayer {
  kind: "layer" | "convective"; genus: string; etage: "low" | "mid" | "high" | null; species: string[];
  base_agl_m: number; base_uncertainty_m: Num; base_ft: number; base_fl: Num; top_amsl_m: number; top_fl: Num;
  oktas: Num; amount: "FEW" | "SCT" | "BKN" | "OVC" | null;
}
export interface CloudsPayload {
  lat: number; lon: number; elevation_m: number; layers: CloudLayer[]; metar: string;
  etage_bounds_fl: { low_mid: number; mid_high: number } | null; ceiling_m: Num; ceiling_ft: Num;
  convective: { class: number; label: string; top_m: Num; top_temp_k: Num };
  cloud_top_teff_k: Num; column_condensate: Num; tcc: Num; cloud_cover_bias: Num;
  cloud_covers: { low: Num; mid: Num; high: Num; total_diag: Num };
  genus: { low: string | null; mid: string | null; high: string | null };
  scientific_status: Record<string, string>; cloud_profile: { name: string; version: string };
  run_cloud_status: string | null; step_consistency: CloudConsistency | null; accumulation_interval_h: Num;
  provenance: Provenance;
}
export interface CloudsSeriesPoint {
  step: number; valid_time: string; missing: boolean;
  genus?: { low: string | null; mid: string | null; high: string | null };
  convective_class?: Num; ceiling_m?: Num; cloud_cover_total_diag?: Num;
}
export interface CloudsSeries { lat: number; lon: number; points: CloudsSeriesPoint[] }
export interface RegistryLayer {
  name: string; label: string; unit: string; per_level: boolean; equation: string; source: string; status: string;
}
export interface Registry {
  layers: Record<string, RegistryLayer>; classes: { upper_bound: number | null; label: string }[];
  profile: { name: string; version: string; weights: Record<string, number>; min_present_weight: number };
  cloud_profile: Record<string, unknown>; codes: Record<string, unknown>; summary_thresholds: Record<string, unknown>;
  attribution: string; license: string;
}
export interface WmsLayer { layer: string; label: string; group: string; attribution: string }
export interface WmsTimes { layer: string; label: string; times: string[]; attribution: string }
