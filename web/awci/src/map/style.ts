/** MapLibre style with no external tile server: embedded Natural Earth basemap and a local graticule. */
import type { StyleSpecification } from "maplibre-gl";
import { API_BASE } from "../api/client";

export interface Bounds { west: number; south: number; east: number; north: number }
interface LineCollection {
  type: "FeatureCollection";
  features: { type: "Feature"; properties: { kind: string }; geometry: { type: "LineString"; coordinates: [number, number][] } }[];
}

/** Meridians and parallels every `stepDeg` degrees inside `b` (points every 1 degree so they curve in Mercator). */
export function graticule(b: Bounds, stepDeg: number): LineCollection {
  const features: LineCollection["features"] = [];
  const first = (v: number) => Math.ceil(v / stepDeg) * stepDeg;
  for (let lon = first(b.west); lon <= b.east; lon += stepDeg) {
    const coordinates: [number, number][] = [];
    for (let lat = b.south; lat <= b.north; lat += 1) coordinates.push([lon, lat]);
    features.push({ type: "Feature", properties: { kind: "meridian" }, geometry: { type: "LineString", coordinates } });
  }
  for (let lat = first(b.south); lat <= b.north; lat += stepDeg) {
    const coordinates: [number, number][] = [];
    for (let lon = b.west; lon <= b.east; lon += 1) coordinates.push([lon, lat]);
    features.push({ type: "Feature", properties: { kind: "parallel" }, geometry: { type: "LineString", coordinates } });
  }
  return { type: "FeatureCollection", features };
}

export function wmsTileUrl(layer: string, time: string): string {
  const q = new URLSearchParams({ layer, time, width: "256", height: "256" });
  return `${API_BASE}/wms?${q.toString()}&bbox={bbox-epsg-3857}`; // MapLibre token must stay unencoded
}

export const MAP_COLORS = {
  sea: "#0b1220", land: "#141d31", coast: "#3a4a6b", border: "#56617a", graticule: "rgba(255,255,255,0.07)",
} as const;

export function baseStyle(b: Bounds): StyleSpecification {
  const margin = 10;
  const wide = { west: b.west - margin, south: b.south - margin, east: b.east + margin, north: b.north + margin };
  return {
    version: 8,
    sources: {
      land: { type: "geojson", data: "/basemap/land.geojson" },
      coastline: { type: "geojson", data: "/basemap/coastline.geojson" },
      borders: { type: "geojson", data: "/basemap/borders.geojson" },
      graticule: { type: "geojson", data: graticule(wide, 5) as never },
    },
    layers: [
      { id: "sea", type: "background", paint: { "background-color": MAP_COLORS.sea } },
      { id: "land", type: "fill", source: "land", paint: { "fill-color": MAP_COLORS.land } },
      { id: "graticule", type: "line", source: "graticule", paint: { "line-color": MAP_COLORS.graticule, "line-width": 0.6 } },
      { id: "coastline", type: "line", source: "coastline", paint: { "line-color": MAP_COLORS.coast, "line-width": 0.8 } },
      { id: "borders", type: "line", source: "borders",
        paint: { "line-color": MAP_COLORS.border, "line-width": 0.6, "line-dasharray": [3, 2] } },
    ],
  };
}
