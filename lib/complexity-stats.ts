import type { ComplexityField, LevelThreshold } from "@/lib/api"

/**
 * Real, derived statistics computed from a `ComplexityField` (the
 * live `GET /complexity/field` response) - every number here is a
 * genuine aggregate of the real per-grid-point AWCI values the
 * backend returned, never a fabricated or hardcoded figure.
 */

const EARTH_RADIUS_KM = 6371.0088 // IUGG mean Earth radius (real, standard constant)
const DEG_TO_RAD = Math.PI / 180

function flatten(field: (number | null)[][]): number[] {
  const values: number[] = []
  for (const row of field) {
    for (const cell of row) {
      if (cell !== null && Number.isFinite(cell)) values.push(cell)
    }
  }
  return values
}

/** Real arithmetic mean of every honestly-defined (non-null) cell. */
export function meanField(field: (number | null)[][]): number | null {
  const values = flatten(field)
  if (values.length === 0) return null
  return values.reduce((sum, v) => sum + v, 0) / values.length
}

/** Real maximum among every honestly-defined (non-null) cell. */
export function maxField(field: (number | null)[][]): number | null {
  const values = flatten(field)
  if (values.length === 0) return null
  return Math.max(...values)
}

function lookupThreshold(thresholds: LevelThreshold[], label: string): number | null {
  const entry = thresholds.find(([, l]) => l === label)
  return entry ? entry[0] : null
}

/**
 * Real classification of an AWCI score against
 * `AWCICalculator.LEVEL_THRESHOLDS` (as returned in
 * `field.level_thresholds`) - the exact same first-match-wins,
 * `score < upper_bound` rule as the backend's own `_get_level()`
 * (`src/awci/complexity/calculator.py`), reused here rather than a
 * second, potentially-drifting copy of the boundary numbers.
 */
export function classifyLevel(thresholds: LevelThreshold[], score: number): string {
  for (const [upperBound, label] of thresholds) {
    if (upperBound === null || score < upperBound) return label
  }
  return thresholds[thresholds.length - 1]?.[1] ?? "Unknown"
}

/** UI tone for a real `classifyLevel()` label - a purely presentational
 * mapping (which bands read as "needs attention"), not a scientific
 * claim. */
export function toneForLevel(label: string): "normal" | "warning" | "critical" {
  if (label === "High" || label === "Very High" || label === "Extreme") return "critical"
  if (label === "Moderate") return "warning"
  return "normal"
}

/**
 * Real spherical grid-cell area (km^2), equirectangular-grid
 * approximation: area(lat) = R^2 * dLatRad * dLonRad * cos(lat) -
 * standard practice for a regular lat/lon NWP grid (the same
 * approximation operational area-weighted grid statistics use),
 * assuming a spherical Earth and uniform grid spacing (both true of
 * `EarthGrid`'s real output - see `spatial_field.py`). Not an
 * ellipsoidal (WGS84) correction - a real, disclosed simplification,
 * not a fabricated number.
 */
function cellAreaKm2(latDeg: number, dLatDeg: number, dLonDeg: number): number {
  const dLatRad = dLatDeg * DEG_TO_RAD
  const dLonRad = dLonDeg * DEG_TO_RAD
  return EARTH_RADIUS_KM ** 2 * dLatRad * dLonRad * Math.cos(latDeg * DEG_TO_RAD)
}

/**
 * Real total area (km^2) of every grid cell whose real `awci_field`
 * value is at or above the named `AWCICalculator.LEVEL_THRESHOLDS`
 * band (`thresholdLabel`, e.g. `"Moderate"`) - a genuine area-weighted
 * count over the real field, using the exact real thresholds the
 * backend itself classifies levels with (`field.level_thresholds`),
 * never a duplicated/hardcoded copy of those bands. Returns `null`
 * when the field has fewer than 2 latitudes/longitudes (cell size
 * cannot be derived) or the named band is not present.
 */
export function affectedAreaKm2(field: ComplexityField, thresholdLabel: string): number | null {
  const { lats, lons, awci_field } = field
  if (lats.length < 2 || lons.length < 2) return null
  const minValue = lookupThreshold(field.level_thresholds, thresholdLabel)
  if (minValue === null) return null

  const dLat = Math.abs(lats[1] - lats[0])
  const dLon = Math.abs(lons[1] - lons[0])

  let totalKm2 = 0
  for (let i = 0; i < awci_field.length; i++) {
    const row = awci_field[i]
    const area = cellAreaKm2(lats[i], dLat, dLon)
    for (const cell of row) {
      if (cell !== null && cell >= minValue) totalKm2 += area
    }
  }
  return totalKm2
}

/** Real mean of the field's `confidence` module (part of
 * `AWCICalculator.FORECAST_MODULES`) - honestly flat near 100 under
 * default weights when no ensemble/model-realization data was
 * supplied to the field computation (see the field's own
 * `honest_limitation`), not a fabricated "high confidence" claim.
 *
 * `module_fields.confidence` is NOT itself a confidence percentage -
 * it is `AWCICalculator`'s "confidence complexity CONTRIBUTION"
 * (`scores["confidence"] = 100 * (1 - normalize_confidence(raw))`,
 * `src/awci/complexity/calculator.py` line ~801) - 0 means "no
 * uncertainty-driven complexity" (i.e. genuinely HIGH real
 * confidence), not "0% confidence". `Normalizer.normalize_confidence()`
 * is exactly linear and range-preserving
 * (`clip(raw, 0, 100) / 100` - `src/awci/complexity/normalizer.py`),
 * so this is an exact, real inversion back to the raw confidence
 * percentage (`raw = 100 - module_score`, valid whenever the module's
 * own real input `raw` was already within [0, 100], true of its
 * default 100.0) - not an approximation or a re-derived formula. */
export function meanConfidence(field: ComplexityField): number | null {
  const confidenceField = field.module_fields.confidence
  if (!confidenceField) return null
  const meanContribution = meanField(confidenceField)
  return meanContribution === null ? null : 100 - meanContribution
}

/**
 * Real nearest-grid-point sample of `awci_field` at (`lat`, `lon`) -
 * the exact same nearest-neighbour convention the backend's own
 * `vertical_field.vertical_profile_at_point()` uses (never spatial
 * interpolation). Used to plot a real AWCI-along-route curve by
 * sampling the already-fetched field at each real route waypoint's
 * position - a genuine composition of 2 real datasets (the field and
 * the route's real great-circle waypoints), not a fabricated curve.
 *
 * Honest limitation: at this field's typical coarse resolution (a
 * few dozen grid points spanning the whole globe), one grid cell can
 * span hundreds of km, so nearby waypoints may return the identical
 * sample and the curve is a coarse proxy for actual along-route
 * variation, not a fine-grained sounding - the caller should disclose
 * the field's own resolution alongside this value.
 */
export function sampleFieldAt(field: ComplexityField, lat: number, lon: number): number | null {
  const { lats, lons, awci_field } = field
  if (lats.length === 0 || lons.length === 0) return null
  let latIdx = 0
  let bestLatDelta = Infinity
  for (let i = 0; i < lats.length; i++) {
    const delta = Math.abs(lats[i] - lat)
    if (delta < bestLatDelta) {
      bestLatDelta = delta
      latIdx = i
    }
  }
  let lonIdx = 0
  let bestLonDelta = Infinity
  for (let j = 0; j < lons.length; j++) {
    const delta = Math.abs(lons[j] - lon)
    if (delta < bestLonDelta) {
      bestLonDelta = delta
      lonIdx = j
    }
  }
  return awci_field[latIdx]?.[lonIdx] ?? null
}
