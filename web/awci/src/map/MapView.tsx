import * as maplibregl from "maplibre-gl";
import type { CanvasSource, GeoJSONSource, Map as MlMap } from "maplibre-gl";
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

const EMPTY = { type: "FeatureCollection" as const, features: [] };

const domainCorners = (d: Domain): [[number, number], [number, number], [number, number], [number, number]] =>
  [[d.west, d.north], [d.east, d.north], [d.east, d.south], [d.west, d.south]];

const spacingForZoom = (z: number) => (z < 4 ? 3 : z < 6 ? 1.5 : 0.75);

export function MapView({ domain, field, def, awciBounds, wind, overlays, point, opacity, onPick, onOverlayError }: Props) {
  const container = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MlMap | null>(null);
  const pickRef = useRef(onPick);
  const overlayErrorRef = useRef(onOverlayError);
  const overlayLayers = useRef(new Map<string, string>()); // map source id -> WMS layer name
  // The field is drawn into one canvas read by a MapLibre canvas source: no PNG encode/decode per step.
  const canvasRef = useRef<HTMLCanvasElement>(document.createElement("canvas"));
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
      canvasRef.current.width = 1;
      canvasRef.current.height = 1;
      map.addSource("field", { type: "canvas", canvas: canvasRef.current, coordinates: domainCorners(domain), animate: false });
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
    map.on("click", (e) => pickRef.current(e.lngLat.lat, e.lngLat.lng));
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
    const canvas = canvasRef.current;
    if (canvas.width !== image.width || canvas.height !== image.height) {
      canvas.width = image.width;
      canvas.height = image.height;
    }
    canvas.getContext("2d")?.putImageData(new ImageData(new Uint8ClampedArray(image.data), image.width, image.height), 0, 0);
    const source = map.getSource("field") as CanvasSource;
    source.setCoordinates(image.coordinates); // also makes a static canvas source re-read its pixels
    source.play();
    requestAnimationFrame(() => source.pause());
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
