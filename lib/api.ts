/**
 * Real, typed HTTP client for the AWCI FastAPI backend
 * (`src/awci/api/app.py`, routers under `src/awci/api/routes/`).
 *
 * Every type below mirrors the real Python dataclass a route returns
 * (serialized field-for-field by `acf.utils.serialization.to_json_safe`
 * - dataclasses become plain objects with the same field names,
 * `datetime` becomes an ISO string, `bytes`/`bytearray` becomes a
 * base64 string). Nothing here is invented: a field is optional/`null`
 * exactly where the backend dataclass itself allows `None`, and no
 * endpoint synthesizes a fallback value when a real fetch fails -
 * failure is reported honestly (`is_real_data: false`, or a thrown
 * `ApiError`) for the UI to render as an explicit error/empty state,
 * never as fabricated data.
 */

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8010").replace(/\/+$/, "")

export class ApiError extends Error {
  readonly status: number
  readonly url: string

  constructor(message: string, status: number, url: string) {
    super(message)
    this.name = "ApiError"
    this.status = status
    this.url = url
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${path}`
  let response: Response
  try {
    response = await fetch(url, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    })
  } catch (cause) {
    const reason = cause instanceof Error ? cause.message : String(cause)
    throw new ApiError(`Network error reaching AWCI API at ${url}: ${reason}`, 0, url)
  }

  if (!response.ok) {
    let detail = response.statusText
    try {
      const body = await response.json()
      detail = typeof body?.detail === "string" ? body.detail : JSON.stringify(body)
    } catch {
      // Body wasn't JSON (or was empty) - fall back to statusText above.
    }
    throw new ApiError(detail, response.status, url)
  }

  return (await response.json()) as T
}

function query(params: Record<string, string | number | boolean | undefined>): string {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) search.set(key, String(value))
  }
  const qs = search.toString()
  return qs ? `?${qs}` : ""
}

// --------------------------------------------------------------------- /complexity

/**
 * Real inputs to `AWCICalculator.calculate()`
 * (`src/awci/complexity/calculator.py`). Every key is optional at the
 * HTTP layer (the backend fills gaps with its own real, documented
 * module defaults) but should be supplied with real observed/forecast
 * values whenever available - never a guessed constant from the UI.
 */
export interface ComplexityInput {
  temperature?: number
  specific_humidity?: number
  wind_speed?: number
  cape?: number
  cin?: number
  precipitation?: number
  pressure?: number
  altitude?: number
  confidence?: number
  temporal_change?: number
  ensemble_members?: number
  model_realizations?: number
  [key: string]: number | undefined
}

export interface ComplexityScore {
  awci: number
  decomposition: Record<string, number>
  level: string
  confidence: number
  module_scores: Record<string, number>
  interaction_scores: Record<string, number>
  explanation: string[]
  physical_score: number
  forecast_score: number
  physical_level: string
  forecast_level: string
}

export function getComplexityScore(input: ComplexityInput): Promise<ComplexityScore> {
  return request<ComplexityScore>("/complexity/score", {
    method: "POST",
    body: JSON.stringify(input),
  })
}

export interface ComplexityFieldParams {
  model?: "AROME" | "ALADIN" | "ARPEGE"
  level?: number
  steps?: number
  seed?: number
  n_lat?: number
  n_lon?: number
  /** Real opt-in physics, each a genuine extra per-point computation
   * (see GET /complexity/field's own docstring for measured real
   * cost) - default off, matching the backend's own default. */
  compute_convective_energy?: boolean
  compute_wind_shear?: boolean
  compute_precipitation_phase?: boolean
  compute_ceiling?: boolean
  compute_visibility?: boolean
}

/** Real classification band from `AWCICalculator.LEVEL_THRESHOLDS` -
 * `upper_bound: null` means the top band (no upper bound, "Extreme"). */
export type LevelThreshold = [number | null, string]

/** Real 2D Complexity(x, y) field - mirrors the JSON built by
 * `GET /complexity/field`. `*_field` values are `lats.length` rows of
 * `lons.length` columns; a `null` cell is a real, honestly-undefined
 * value (the underlying engine's own `np.nan`), never a fabricated 0. */
export interface ComplexityField {
  lats: number[]
  lons: number[]
  model: string
  level: number
  awci_field: (number | null)[][]
  physical_field: (number | null)[][]
  forecast_field: (number | null)[][]
  module_fields: Record<string, (number | null)[][]>
  level_thresholds: LevelThreshold[]
  status: string
  is_real_data: boolean
  honest_limitation: string
  /** Present only when `compute_wind_shear: true` was requested -
   * real bulk wind shear (m/s), not a 0-100 score. */
  wind_shear_field?: (number | null)[][]
  /** Present only when `compute_precipitation_phase: true` was
   * requested - real severity in [0, 1] (multiply by 100 to compare
   * with the other 0-100 module scores). */
  precipitation_phase_severity_field?: (number | null)[][]
}

export function getComplexityField(params: ComplexityFieldParams = {}): Promise<ComplexityField> {
  const {
    model,
    level,
    steps,
    seed,
    n_lat,
    n_lon,
    compute_convective_energy,
    compute_wind_shear,
    compute_precipitation_phase,
    compute_ceiling,
    compute_visibility,
  } = params
  return request(
    `/complexity/field${query({
      model,
      level,
      steps,
      seed,
      n_lat,
      n_lon,
      compute_convective_energy,
      compute_wind_shear,
      compute_precipitation_phase,
      compute_ceiling,
      compute_visibility,
    })}`,
  )
}

export interface VerticalProfileParams {
  lat: number
  lon: number
  model?: "AROME" | "ALADIN" | "ARPEGE"
  steps?: number
  seed?: number
  n_lat?: number
  n_lon?: number
  n_levels?: number
}

/** Real Complexity(z) column - mirrors the JSON built by
 * `GET /complexity/vertical-profile`. Ordered surface (index 0) to
 * top of atmosphere; `lat`/`lon` are the real grid point actually
 * used (nearest-neighbour match, not necessarily the requested point
 * exactly - see the route's own docstring). */
export interface VerticalProfile {
  lat: number
  lon: number
  awci_profile: (number | null)[]
  physical_profile: (number | null)[]
  forecast_profile: (number | null)[]
  pressure_profile_hpa: number[]
  temperature_profile: number[]
  wind_speed_profile: number[]
  model: string
  n_levels: number
  status: string
  is_real_data: boolean
  honest_limitation: string
}

export function getVerticalProfile(params: VerticalProfileParams): Promise<VerticalProfile> {
  const { lat, lon, model, steps, seed, n_lat, n_lon, n_levels } = params
  return request(`/complexity/vertical-profile${query({ lat, lon, model, steps, seed, n_lat, n_lon, n_levels })}`)
}

// --------------------------------------------------------------------- /airports

/** Mirrors `awci.knowledge.airports.airport_database.AirportInfo`. */
export interface AirportInfo {
  icao_code: string
  iata_code: string
  name: string
  city: string
  country: string
  latitude: number
  longitude: number
  elevation_ft: number
  runways: { identifier: string; length_m: number; width_m: number; surface: string }[]
  ils_categories: string[]
  magnetic_variation_deg: number
  code_letter: string
}

export function listAirports(): Promise<AirportInfo[]> {
  return request("/airports")
}

export interface RunwayWindAssessment {
  runway_end: string
  heading_deg: number
  headwind_kt: number
  crosswind_kt: number
  crosswind_direction: string
}

export function getRunwayWind(
  icaoOrIata: string,
  windDirDeg: number,
  windSpeedKt: number,
): Promise<Record<string, RunwayWindAssessment>> {
  return request(`/airports/${icaoOrIata}/runways${query({ wind_dir_deg: windDirDeg, wind_speed_kt: windSpeedKt })}`)
}

/** Mirrors `awci.airport.weather.AirportWeatherSnapshot`. */
export interface AirportWeatherSnapshot {
  icao_code: string
  is_real_data: boolean
  status: string
  ceiling_height_ft: number | null
  ceiling_category: string | null
  visibility_m: number | null
  present_weather_descriptions: string[]
  raw_metar: string | null
}

export function getAirportWeather(icaoCode: string): Promise<AirportWeatherSnapshot> {
  return request(`/airports/${icaoCode}/weather`)
}

// --------------------------------------------------------------------- /flights

/** Mirrors `awci.flight.waypoint.Waypoint`. Position only - see
 * `route_weather.py`'s own docstring: there is no real data source for
 * weather at an arbitrary point along a route. */
export interface Waypoint {
  latitude: number
  longitude: number
  distance_from_origin_km: number
  fraction: number
}

/** Mirrors `awci.flight.route_weather.RouteWeatherBriefing`. */
export interface RouteWeatherBriefing {
  departure_icao: string
  arrival_icao: string
  great_circle_distance_nm: number
  waypoints: Waypoint[]
  departure_weather: AirportWeatherSnapshot
  arrival_weather: AirportWeatherSnapshot
  alternate_weather: Record<string, AirportWeatherSnapshot>
}

export function getRouteWeather(
  depIcao: string,
  arrIcao: string,
  nWaypoints = 10,
): Promise<RouteWeatherBriefing> {
  return request(`/flights/route-weather${query({ dep_icao: depIcao, arr_icao: arrIcao, n_waypoints: nWaypoints })}`)
}

// --------------------------------------------------------------------- /observations

/** Mirrors `awci.knowledge.icao.metar_decoder.METARReport` (and
 * TAF/SIGMET reports carry their own distinct shape - typed loosely
 * here since this client doesn't currently render TAF/SIGMET detail). */
export interface METARReport {
  raw_text: string
  icao_code: string
  day: number | null
  hour: number | null
  minute: number | null
  is_auto: boolean
  wind_direction_deg: number | null
  wind_variable_direction: boolean
  wind_speed_kt: number | null
  wind_gust_kt: number | null
  wind_variable_from_deg: number | null
  wind_variable_to_deg: number | null
  visibility_m: number | null
  cavok: boolean
  rvr: Record<string, unknown>[]
  present_weather: string[]
  cloud_layers: { coverage: string; base_ft: number; type: string | null }[]
  vertical_visibility_ft: number | null
  temperature_c: number | null
  dewpoint_c: number | null
  qnh_hpa: number | null
  trend: string | null
}

/** One decoded TAF change-group period - mirrors the dicts in
 * `awci.knowledge.icao.taf_decoder.TAFReport.periods`. */
export interface TAFPeriod {
  change_type: string
  probability: number | null
  from_day: number | null
  from_hour: number | null
  from_minute: number | null
  until_day: number | null
  until_hour: number | null
  wind_direction_deg: number | null
  wind_variable: boolean
  wind_speed_kt: number | null
  wind_gust_kt: number | null
  visibility_m: number | null
  cavok: boolean
  present_weather: string[]
  cloud_layers: { coverage: string; base_ft: number; type: string | null }[]
  vertical_visibility_ft: number | null
}

/** Mirrors `awci.knowledge.icao.taf_decoder.TAFReport`. */
export interface TAFReport {
  raw_text: string
  icao_code: string
  is_amended: boolean
  is_corrected: boolean
  issue_day: number | null
  issue_hour: number | null
  issue_minute: number | null
  valid_from_day: number | null
  valid_from_hour: number | null
  valid_until_day: number | null
  valid_until_hour: number | null
  periods: TAFPeriod[]
}

export interface LiveReport {
  raw_text: string | null
  decoded: METARReport | TAFReport | Record<string, unknown> | null
  error: string | null
}

export interface LiveStationBundle {
  icao_code: string
  metar: LiveReport
  taf: LiveReport
}

/** One real Pilot Report, raw fields as returned by NOAA
 * aviationweather.gov's PIREP API (`awci.data.connectors.pirep_reports`). */
export interface PIREPReport {
  receiptTime: string
  obsTime: number
  icaoId: string | null
  acType: string | null
  lat: number
  lon: number
  fltLvl: number | null
  fltLvlType: string | null
  wxString: string | null
  temp: number | null
  wdir: number | null
  wspd: number | null
  icgInt1: string | null
  icgType1: string | null
  tbInt1: string | null
  tbType1: string | null
  tbFreq1: string | null
  brkAction: string | null
  pirepType: string | null
  rawOb: string
  [key: string]: unknown
}

/** Mirrors `awci.data.connectors.pirep_reports.PIREPFetchResult`. */
export interface PIREPFetchResult {
  is_real_data: boolean
  status: string
  report_count: number
  reports: PIREPReport[]
  fetched_at: number
}

/** Mirrors `awci.data.connectors.nexrad_stations.NexradFetchResult`. */
export interface NexradFetchResult {
  is_real_data: boolean
  status: string
  stations_operational: number
  stations_total: number
  stations: { id: string; operational: boolean; mode: string | null; last_received: string | null }[]
  fetched_at: number
}

/** Mirrors `awci.data.connectors.eumetsat_mtg.MTGFetchResult`.
 * `image_bytes` is base64-encoded by `to_json_safe` - decode with
 * `atob()`/a data URI (`data:image/jpeg;base64,${image_bytes}`) to
 * display it. */
export interface MTGFetchResult {
  is_real_data: boolean
  status: string
  authenticated: boolean
  image_bytes: string | null
  product_id: string | null
  collection: string | null
  observation_start: string | null
  observation_end: string | null
  source_url: string | null
  fetched_at: number | null
}

/** Mirrors `awci.observations.hub.ObservationsSnapshot`. */
export interface ObservationsSnapshot {
  icao_code: string
  station: LiveStationBundle
  sigmets: LiveReport[]
  pireps: PIREPFetchResult
  radar: NexradFetchResult
  satellite: MTGFetchResult
  fetched_at: number
}

export function getObservations(icaoCode: string): Promise<ObservationsSnapshot> {
  return request(`/observations/${icaoCode}`)
}

// --------------------------------------------------------------------- /hazards

/** Mirrors `awci.knowledge.hazards.aviation_hazards.AviationHazard`. */
export interface AviationHazard {
  key: string
  name: string
  category: string
  physical_explanation: string
  governing_equation: string
  icao_thresholds: Record<string, string>
  operational_impacts: string[]
  flight_recommendations: string[]
  references: string[]
}

export function listHazards(): Promise<string[]> {
  return request("/hazards")
}

export function getHazardDetail(key: string): Promise<AviationHazard> {
  return request(`/hazards/${key}`)
}

// --------------------------------------------------------------------- /health

export interface HealthStatus {
  status: string
  [key: string]: unknown
}

export function getHealth(): Promise<HealthStatus> {
  return request("/health")
}
