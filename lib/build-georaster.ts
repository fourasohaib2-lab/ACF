import type { GeoRaster } from "georaster"
import type { ComplexityField } from "@/lib/api"

/**
 * Real `GeoRaster` built from a `ComplexityField` module - feeds
 * `georaster-layer-for-leaflet`'s `GeoRasterLayer`, which then does
 * the actual real geographic reprojection/tiling, replacing the
 * hand-rolled equirectangular canvas this module's earlier draft
 * used. Every value is the real backend result at its real
 * `EarthGrid` grid point; `null`/non-finite cells (the field's own
 * honest "not computed" - never a fabricated 0) become `NaN`, the
 * georaster `noDataValue`, and render as fully transparent.
 */
export async function buildFieldGeoraster(field: ComplexityField, moduleKey = "awci"): Promise<GeoRaster | null> {
  const grid = moduleKey === "awci" ? field.awci_field : field.module_fields[moduleKey]
  if (!grid || field.lats.length === 0 || field.lons.length === 0) return null

  const rows = field.lats.length
  const cols = field.lons.length
  // Real, uniform grid spacing (EarthGrid produces an evenly-spaced
  // lat/lon grid - see spatial_field.py).
  const pixelWidth = cols > 1 ? Math.abs(field.lons[1] - field.lons[0]) : 360
  const pixelHeight = rows > 1 ? Math.abs(field.lats[1] - field.lats[0]) : 180
  const xmin = field.lons[0] - pixelWidth / 2
  const ymax = field.lats[rows - 1] + pixelHeight / 2

  // georaster's row 0 is the northernmost row; the backend's lats
  // ascend south -> north (see EarthGrid), so reverse rows here.
  const band: number[][] = []
  for (let i = rows - 1; i >= 0; i--) {
    band.push(grid[i].map((v) => (v === null || !Number.isFinite(v) ? Number.NaN : v)))
  }

  const parseGeoraster = (await import("georaster")).default
  return parseGeoraster([band], {
    noDataValue: Number.NaN,
    projection: 4326,
    xmin,
    ymax,
    pixelWidth,
    pixelHeight,
  })
}
