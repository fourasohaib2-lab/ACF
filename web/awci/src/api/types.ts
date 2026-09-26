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

// ---- SP3: aeronautical observations (AWC, public domain) and verification ----
export type FlightCategory = "VFR" | "MVFR" | "IFR" | "LIFR";
export type CeilingStatus = "value" | "none" | "none_below_5000" | "unknown";

export interface MetarObs {
  time: string; kind: string; raw: string; auto: boolean; visibility_m: number | null; weather: string[];
  cavok: boolean; no_sig_cloud: string | null;
  layers: { cover: string; base_ft: number | null; type: string | null }[];
  vertical_visibility_ft: number | null; ceiling_status: CeilingStatus; ceiling_ft: number | null;
  convective: boolean | null; flight_category: FlightCategory | null;
}
export interface Airport {
  icao: string; name: string; lat: number; lon: number; elev_m: number; metar: boolean; taf: boolean;
  observation: MetarObs | null;
}
export interface AirportsPayload {
  time: string; tolerance_min: number; airports: Airport[]; ingested_at: string | null; attribution: string;
}
export interface TafPeriod {
  from: string; to: string | null; change: string | null; probability: number | null;
  visibility: string | number | null; weather: string | null;
  clouds: { cover: string | null; base_ft: number | null; type: string | null }[];
}
export interface Taf { icao: string; issued: string | null; valid_from: string; valid_to: string; raw: string; periods: TafPeriod[] }
export interface AirportModelPoint {
  step: number; valid_time: string; missing: boolean; ceiling_ft: number | null; convective_class: number | null;
  surface_height_m: number | null; genus_low: string | null; cloud_cover_low: number | null;
}
export interface AirportPair {
  step: number; valid_time: string; observation: MetarObs | null; model_ceiling_ft: number | null;
  model_convective: boolean | null;
}
export interface AirportDetail {
  station: Omit<Airport, "observation">; grid: { lat: number; lon: number }; dz_m: number | null;
  metars: MetarObs[]; taf: Taf | null; model: AirportModelPoint[]; pairs: AirportPair[]; run: string;
  attribution: string; model_attribution: string | null;
}
export interface SigmetProps {
  hazard: "TS" | "TURB" | "ICE" | "VA" | "TC" | "MTW"; qualifier: string | null; fir: string | null;
  fir_name: string | null; series: string | null; base_ft: number | null; top_ft: number | null;
  valid_from: string; valid_to: string; direction: string | null; speed_kt: string | null; change: string | null;
  raw: string; received: string | null;
}
export interface SigmetFeature { type: "Feature"; geometry: { type: "Polygon"; coordinates: number[][][] }; properties: SigmetProps }
export interface SigmetCollection {
  type: "FeatureCollection"; features: SigmetFeature[]; time: string; ingested_at: string | null; attribution: string;
}
export interface ScoreTable {
  a: number; b: number; c: number; d: number; n: number; observed_events: number; forecast_events: number;
  pod: number | null; far: number | null; csi: number | null; bias: number | null; ets: number | null; sufficient: boolean;
}
export interface Verification {
  domain: string; run: string; valid_from: string; valid_to: string; generated_at: string;
  parameters: { tolerance_min: number; max_elevation_diff_m: number; thresholds_ft: number[]; min_observed_events: number;
    convective_min_class: number; status: string };
  stations: { total: number; with_pairs: number }; pairs: number; exclusions: Record<string, number>;
  events: Record<string, { total: ScoreTable; by_lead: (ScoreTable & { lead: string })[] }>;
  ceiling_base_error_ft: { n: number; mean_error: number | null; mae: number | null; definition: string };
  observed: string; forecast: string; observations_ingested_at: string | null;
}

// ---- SP5: IFS ENS probabilities (count / n over 50 perturbed members) ----
export type EnsProduct = "p_awci_high" | "p_cloud_bkn" | "p_icing" | "p_cat_moderate" | "p_convection" | "p_ceiling_1500ft";
export interface EnsMeta {
  run: string; steps: number[]; missing_steps: number[]; valid_times: string[]; members_requested: number[];
  members_used: Record<string, number>; failed_members: Record<string, number[]>; products: Record<string, { dims: string }>;
  attribution: string; profile_version: string; cloud_profile_version: string; awci_high_lower_bound: number;
}
export interface EnsRun { run: string; status: string; steps: number[]; missing_steps: number[]; members_used: Record<string, number> }
export interface EnsPointStep {
  step: number; valid_time: string; missing: boolean; members: number;
  probabilities: Record<EnsProduct, number | null> | null; awci_mean: number | null; awci_std: number | null;
}
export interface EnsPoint { lat: number; lon: number; level_hpa: number; points: EnsPointStep[]; run: string; members_requested: number; attribution: string }

// ---- SP5b: probabilistic verification of the ENS against METAR ----
export interface ReliabilityBin { lower: number; upper: number; n: number; mean_forecast: number | null; observed_frequency: number | null }
export interface BrierScores {
  n: number; observed_events: number; sufficient: boolean; observed_frequency?: number; mean_probability?: number;
  brier: number | null; fair_brier: number | null; uncertainty: number | null; reliability: number | null;
  resolution: number | null; decomposition_residual: number | null; bss_climatology: number | null;
  brier_deterministic: number | null; skill_vs_deterministic: number | null; members_min?: number; members_max?: number;
}
export interface EnsVerification {
  domain: string; run: string; generated_at: string; samples: number; exclusions: Record<string, number>;
  parameters: { tolerance_min: number; max_elevation_diff_m: number; min_observed_events: number; probability_bins: number[];
    ceiling_threshold_ft: number };
  events: Record<string, { total: BrierScores & { diagram: ReliabilityBin[] }; by_step: (BrierScores & { step: number })[] }>;
  cloud_profiles: { ens: string | null; deterministic: string | null }; like_for_like: boolean;
  observed: string; forecast: string; observations_ingested_at: string | null;
}

// ---- SP4: route cross-section and route meteogram ----
export interface RouteWaypoint { index: number; distance_km: number; lat: number; lon: number }
interface RouteGeometry {
  length_km: number; spacing_km: number; distance_km: number[]; lat: number[]; lon: number[]; grid_lat: number[]; grid_lon: number[];
  waypoints: RouteWaypoint[]; levels_hpa: number[]; flight_levels: number[];
}
export interface RouteSection extends RouteGeometry {
  layer: string; unit: string; values: (number | null)[][]; surface_pressure_hpa: (number | null)[] | null;
  surface_height_m: (number | null)[] | null; provenance: Provenance;
}
export interface RouteMeteogramStep {
  step: number; valid_time: string; missing: boolean; awci_max: (number | null)[] | null; awci_median: (number | null)[] | null;
  frac_awci_high: (number | null)[] | null; frac_icing: (number | null)[] | null; frac_cat_moderate: (number | null)[] | null;
  frac_cloud_bkn: (number | null)[] | null;
}
export interface RouteMeteogram extends RouteGeometry { awci_high_lower_bound: number; steps: RouteMeteogramStep[]; provenance: Provenance }
