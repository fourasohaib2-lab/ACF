import * as maplibregl from "maplibre-gl";
import type { GeoJSONSource, ImageSource, Map as MlMap, MapMouseEvent } from "maplibre-gl";
// MapLibre 6 runs its tile/GeoJSON work in a module worker that the bundler must emit as its own file.
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url";
import { useEffect, useRef, useState } from "react";
import type { Domain, FieldData } from "../api/types";
import { fr } from "../i18n/fr";
import { gridEdges, renderField } from "./fieldRaster";
import { colorFn, type LayerDef } from "./layers";
import { streamlineFeatures, type WindGrid } from "./streamlines";
import { baseStyle, wmsTileUrl } from "./style";

export interface Overlay { layer: string; time: string; opacity: number }
interface Props {
  domain: Domain;
  field: FieldData | undefined;
  def: LayerDef;
  awciBounds: number[];
  wind: WindGrid | undefined;
  overlays: Overlay[];
  point: { lat: number; lon: number } | undefined;
  opacity: number;
  onPick: (lat: number, lon: number) => void;
  onOverlayError?: (layer: string) => void;
}

maplibregl.setWorkerUrl(workerUrl);

const EMPTY_PNG = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=";
const EMPTY = { type: "FeatureCollection" as const, features: [] };

const domainCorners = (d: Domain): [[number, number], [number, number], [number, number], [number, number]] =>
  [[d.west, d.north], [d.east, d.north], [d.east, d.south], [d.west, d.south]];

function toDataUrl(data: Uint8ClampedArray, width: number, height: number): string {
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d");
  if (!ctx) return EMPTY_PNG;
  ctx.putImageData(new ImageData(new Uint8ClampedArray(data), width, height), 0, 0);
  return canvas.toDataURL("image/png");
}

const spacingForZoom = (z: number) => (z < 4 ? 3 : z < 6 ? 1.5 : 0.75);

export function MapView({ domain, field, def, awciBounds, wind, overlays, point, opacity, onPick, onOverlayError }: Props) {
  const container = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MlMap | null>(null);
  const pickRef = useRef(onPick);
  const overlayErrorRef = useRef(onOverlayError);
  const overlayLayers = useRef(new Map<string, string>()); // map source id -> WMS layer name
  const [ready, setReady] = useState(false);
  const [spacing, setSpacing] = useState(3);

  useEffect(() => { pickRef.current = onPick; }, [onPick]);
  useEffect(() => { overlayErrorRef.current = onOverlayError; }, [onOverlayError]);

  useEffect(() => {
    if (!container.current) return;
    const map = new maplibregl.Map({
      container: container.current, style: baseStyle(domain), dragRotate: false, pitchWithRotate: false,
      bounds: [[domain.west, domain.south], [domain.east, domain.north]], fitBoundsOptions: { padding: 16 },
      attributionControl: { compact: true, customAttribution: "© ECMWF CC-BY-4.0 · Natural Earth" },
    });
    map.touchZoomRotate.disableRotation();
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    map.addControl(new maplibregl.ScaleControl({ unit: "nautical" }), "bottom-left");
    map.on("load", () => {
      map.addSource("field", { type: "image", url: EMPTY_PNG, coordinates: domainCorners(domain) });
      map.addLayer({ id: "field", type: "raster", source: "field",
        paint: { "raster-resampling": "nearest", "raster-opacity": 0.85, "raster-fade-duration": 0 } }, "coastline");
      map.addSource("streamlines", { type: "geojson", data: EMPTY });
      map.addLayer({ id: "streamlines", type: "line", source: "streamlines",
        paint: { "line-color": "#ffffff", "line-opacity": 0.5, "line-width": 0.8 } });
      map.addSource("point", { type: "geojson", data: EMPTY });
      map.addLayer({ id: "point", type: "circle", source: "point",
        paint: { "circle-radius": 6, "circle-color": "rgba(0,0,0,0)", "circle-stroke-color": "#ffffff", "circle-stroke-width": 2 } });
      setReady(true);
    });
    map.on("click", (e: MapMouseEvent) => pickRef.current(e.lngLat.lat, e.lngLat.lng));
    map.on("zoomend", () => setSpacing(spacingForZoom(map.getZoom())));
    map.on("error", (e) => {
      const id = (e as { sourceId?: string }).sourceId; // set by MapLibre for source (tile) errors
      const layer = id ? overlayLayers.current.get(id) : undefined;
      if (layer) overlayErrorRef.current?.(layer);
    });
    const observer = new ResizeObserver(() => map.resize());
    observer.observe(container.current);
    mapRef.current = map;
    return () => { observer.disconnect(); map.remove(); mapRef.current = null; setReady(false); };
  }, [domain]);

  useEffect(() => {
    const map = mapRef.current;
    if (!ready || !map || !field) return;
    const values = def.render.kind === "genus"
      ? field.values.map((v) => (v === -2 ? Number.NaN : v)) // indeterminate genus is hatched like no-data
      : field.values;
    const image = renderField({ ...field, values }, colorFn(def, awciBounds));
    (map.getSource("field") as ImageSource).updateImage({
      url: toDataUrl(image.data, image.width, image.height), coordinates: image.coordinates,
    });
  }, [ready, field, def, awciBounds]);

  useEffect(() => {
    if (ready) mapRef.current?.setPaintProperty("field", "raster-opacity", opacity);
  }, [ready, opacity]);

  useEffect(() => {
    const source = ready ? (mapRef.current?.getSource("streamlines") as GeoJSONSource | undefined) : undefined;
    source?.setData(wind ? (streamlineFeatures(wind, spacing) as never) : EMPTY);
  }, [ready, wind, spacing]);

  useEffect(() => {
    const source = ready ? (mapRef.current?.getSource("point") as GeoJSONSource | undefined) : undefined;
    source?.setData(point ? { type: "Feature", properties: {}, geometry: { type: "Point", coordinates: [point.lon, point.lat] } } : EMPTY);
  }, [ready, point]);

  useEffect(() => {
    const map = mapRef.current;
    if (!ready || !map) return;
    const wanted = new Map(overlays.map((o) => [`wms-${o.layer}-${o.time}`, o]));
    overlayLayers.current = new Map([...wanted].map(([id, o]) => [id, o.layer]));
    for (const layer of map.getStyle().layers ?? []) {
      if (layer.id.startsWith("wms-") && !wanted.has(layer.id)) {
        map.removeLayer(layer.id);
        map.removeSource(layer.id);
      }
    }
    for (const [id, o] of wanted) {
      if (!map.getSource(id)) {
        map.addSource(id, { type: "raster", tiles: [wmsTileUrl(o.layer, o.time)], tileSize: 256, attribution: fr.observationAttribution });
        map.addLayer({ id, type: "raster", source: id, paint: { "raster-opacity": o.opacity, "raster-fade-duration": 0 } }, "field");
      } else {
        map.setPaintProperty(id, "raster-opacity", o.opacity);
      }
    }
  }, [ready, overlays]);

  const e = field ? gridEdges(field) : undefined;
  return (
    <div className="map-view">
      <div ref={container} className="map-canvas" role="application" tabIndex={0}
           aria-label={`Carte ${def.label}${e ? `, domaine ${e.south.toFixed(1)}–${e.north.toFixed(1)}° N` : ""}. Cliquer pour inspecter un point.`} />
    </div>
  );
}
