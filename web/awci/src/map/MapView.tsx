import * as maplibregl from "maplibre-gl";
import type { CanvasSource, GeoJSONSource, Map as MlMap } from "maplibre-gl";
// MapLibre 6 runs its tile/GeoJSON work in a module worker that the bundler must emit as its own file.
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url";
import { useEffect, useRef, useState } from "react";
import type { Domain, FieldData, SigmetFeature } from "../api/types";
import { fr } from "../i18n/fr";
import { gridEdges, renderField } from "./fieldRaster";
import { CATEGORY_COLORS, HAZARDS, type AirportPoint } from "../lib/aero";
import { colorFn, type LayerDef } from "./layers";
import { streamlineFeatures, type WindGrid } from "./streamlines";
import { baseStyle, wmsTileUrl } from "./style";

export interface Overlay { layer: string; time: string; opacity: number }
interface Props {
  domain: Domain;
  /** Field of the current view only; undefined while it loads (`stale`) or when it failed (canvas cleared). */
  field: FieldData | undefined;
  stale?: boolean;
  def: LayerDef;
  awciBounds: number[];
  wind: WindGrid | undefined;
  overlays: Overlay[];
  point: { lat: number; lon: number } | undefined;
  opacity: number;
  onPick: (lat: number, lon: number) => void;
  onOverlayError?: (layer: string) => void;
  /** Aerodromes with their METAR at the valid time, and SIGMETs valid then (SP3). */
  airports?: { type: "FeatureCollection"; features: AirportPoint[] };
  sigmets?: { type: "FeatureCollection"; features: SigmetFeature[] };
  onPickAirport?: (icao: string) => void;
  /** 3-D volume view: tilted camera and rotation; the 2-D field and streamlines are hidden (SP2B). */
  mode3d?: boolean;
  onMap?: (map: MlMap | null) => void;
}

maplibregl.setWorkerUrl(workerUrl);
// Observation tiles and the forecast API share one origin, where HTTP/1.1 browsers open 6 connections: tiles
// may use at most 3 of them, so a slow EUMETView can never queue /field, /summary or /point behind it.
maplibregl.setMaxParallelImageRequests(3);

const EMPTY = { type: "FeatureCollection" as const, features: [] };

const domainCorners = (d: Domain): [[number, number], [number, number], [number, number], [number, number]] =>
  [[d.west, d.north], [d.east, d.north], [d.east, d.south], [d.west, d.south]];

const spacingForZoom = (z: number) => (z < 4 ? 3 : z < 6 ? 1.5 : 0.75);

const HAZARD_IDS = Object.keys(HAZARDS) as (keyof typeof HAZARDS)[];
const PICK_PX = 6;

export function MapView({ domain, field, stale = false, def, awciBounds, wind, overlays, point, opacity, onPick, onOverlayError,
  airports, sigmets, onPickAirport, mode3d = false, onMap }: Props) {
  const container = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MlMap | null>(null);
  const pickRef = useRef(onPick);
  const overlayErrorRef = useRef(onOverlayError);
  const overlayLayers = useRef(new Map<string, string>()); // map source id -> WMS layer name
  // The field is drawn into one canvas read by a MapLibre canvas source: no PNG encode/decode per step.
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  canvasRef.current ??= document.createElement("canvas");
  const drawnLayer = useRef<string | null>(null); // layer whose values the canvas currently holds
  const [ready, setReady] = useState(false);
  const [spacing, setSpacing] = useState(3);

  useEffect(() => { pickRef.current = onPick; }, [onPick]);
  useEffect(() => { overlayErrorRef.current = onOverlayError; }, [onOverlayError]);
  const onMapRef = useRef(onMap);
  useEffect(() => { onMapRef.current = onMap; }, [onMap]);
  const pickAirportRef = useRef(onPickAirport);
  useEffect(() => { pickAirportRef.current = onPickAirport; }, [onPickAirport]);

  useEffect(() => {
    if (!container.current) return;
    const map = new maplibregl.Map({
      container: container.current, style: baseStyle(domain), dragRotate: false, pitchWithRotate: true, maxPitch: 70,
      bounds: [[domain.west, domain.south], [domain.east, domain.north]], fitBoundsOptions: { padding: 16 },
      attributionControl: { compact: true, customAttribution: "© ECMWF CC-BY-4.0 · Natural Earth" },
    });
    map.touchZoomRotate.disableRotation();
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    map.addControl(new maplibregl.ScaleControl({ unit: "nautical" }), "bottom-left");
    map.on("load", () => {
      canvasRef.current!.width = 1;
      canvasRef.current!.height = 1;
      map.addSource("field", { type: "canvas", canvas: canvasRef.current!, coordinates: domainCorners(domain), animate: false });
      map.addLayer({ id: "field", type: "raster", source: "field",
        paint: { "raster-resampling": "nearest", "raster-opacity": 0.85, "raster-fade-duration": 0 } }, "coastline");
      map.addSource("streamlines", { type: "geojson", data: EMPTY });
      map.addLayer({ id: "streamlines", type: "line", source: "streamlines",
        paint: { "line-color": "#ffffff", "line-opacity": 0.5, "line-width": 0.8 } });
      map.addSource("sigmets", { type: "geojson", data: EMPTY });
      map.addLayer({ id: "sigmet-fill", type: "fill", source: "sigmets",
        paint: { "fill-color": ["match", ["get", "hazard"], ...HAZARD_IDS.flatMap((h) => [h, HAZARDS[h].color]), "#ffffff"] as never,
          "fill-opacity": 0.12 } });
      for (const h of HAZARD_IDS) { // one layer per hazard: MapLibre dash patterns are not data-driven
        map.addLayer({ id: `sigmet-${h}`, type: "line", source: "sigmets", filter: ["==", ["get", "hazard"], h],
          paint: { "line-color": HAZARDS[h].color, "line-width": HAZARDS[h].width, "line-dasharray": HAZARDS[h].dash } });
      }
      map.addSource("airports", { type: "geojson", data: EMPTY });
      map.addLayer({ id: "airports-convective", type: "circle", source: "airports", filter: ["==", ["get", "convective"], true],
        paint: { "circle-radius": 9, "circle-color": "rgba(0,0,0,0)", "circle-stroke-color": CATEGORY_COLORS.LIFR,
          "circle-stroke-width": 2 } });
      map.addLayer({ id: "airports", type: "circle", source: "airports",
        paint: { "circle-radius": 5,
          "circle-color": ["match", ["get", "category"], "VFR", CATEGORY_COLORS.VFR, "MVFR", CATEGORY_COLORS.MVFR,
            "IFR", CATEGORY_COLORS.IFR, "LIFR", CATEGORY_COLORS.LIFR, "rgba(0,0,0,0)"],
          "circle-stroke-color": ["case", ["get", "observed"], "#0b1220", "#8a94a8"], "circle-stroke-width": 1.5 } });
      map.addSource("point", { type: "geojson", data: EMPTY });
      map.addLayer({ id: "point", type: "circle", source: "point",
        paint: { "circle-radius": 6, "circle-color": "rgba(0,0,0,0)", "circle-stroke-color": "#ffffff", "circle-stroke-width": 2 } });
      setReady(true);
    });
    map.on("click", (e) => {
      const box: [[number, number], [number, number]] = [[e.point.x - PICK_PX, e.point.y - PICK_PX], [e.point.x + PICK_PX, e.point.y + PICK_PX]];
      const hit = map.getLayer("airports") ? map.queryRenderedFeatures(box, { layers: ["airports"] })[0] : undefined;
      const icao = hit?.properties?.icao as string | undefined;
      if (icao && pickAirportRef.current) pickAirportRef.current(icao);
      else pickRef.current(e.lngLat.lat, e.lngLat.lng);
    });
    map.on("zoomend", () => setSpacing(spacingForZoom(map.getZoom())));
    map.on("error", (e) => {
      const id = (e as { sourceId?: string }).sourceId; // set by MapLibre for source (tile) errors
      const layer = id ? overlayLayers.current.get(id) : undefined;
      if (layer) overlayErrorRef.current?.(layer);
    });
    const observer = new ResizeObserver(() => map.resize());
    observer.observe(container.current);
    mapRef.current = map;
    onMapRef.current?.(map);
    return () => { observer.disconnect(); onMapRef.current?.(null); map.remove(); mapRef.current = null; setReady(false); };
  }, [domain]);

  useEffect(() => {
    const map = mapRef.current;
    if (!ready || !map) return;
    const canvas = canvasRef.current!;
    const source = map.getSource("field") as CanvasSource;
    const refresh = (coordinates: Parameters<CanvasSource["setCoordinates"]>[0]) => {
      source.setCoordinates(coordinates); // also makes a static canvas source re-read its pixels
      source.play();
      requestAnimationFrame(() => source.pause());
    };
    if (!field) {
      // Loading the same quantity: keep the previous image, dimmed (see opacity). Anything else (another layer,
      // a failed request) must not leave foreign values on the map: clear it.
      if (stale && drawnLayer.current === def.id) return;
      canvas.getContext("2d")?.clearRect(0, 0, canvas.width, canvas.height);
      drawnLayer.current = null;
      refresh(domainCorners(domain));
      return;
    }
    const values = def.render.kind === "genus"
      ? field.values.map((v) => (v === -2 ? Number.NaN : v)) // indeterminate genus is hatched like no-data
      : field.values;
    const image = renderField({ ...field, values }, colorFn(def, awciBounds), 4, { nanTransparent: !!def.nanMeaning });
    if (canvas.width !== image.width || canvas.height !== image.height) {
      canvas.width = image.width;
      canvas.height = image.height;
    }
    canvas.getContext("2d")?.putImageData(new ImageData(image.data as Uint8ClampedArray<ArrayBuffer>, image.width, image.height), 0, 0);
    drawnLayer.current = def.id;
    refresh(image.coordinates);
  }, [ready, field, stale, def, awciBounds, domain]);

  useEffect(() => {
    if (ready) mapRef.current?.setPaintProperty("field", "raster-opacity", stale ? opacity * 0.35 : opacity);
  }, [ready, opacity, stale]);

  useEffect(() => {
    const source = ready ? (mapRef.current?.getSource("streamlines") as GeoJSONSource | undefined) : undefined;
    source?.setData(wind ? (streamlineFeatures(wind, spacing) as never) : EMPTY);
  }, [ready, wind, spacing]);

  useEffect(() => {
    const source = ready ? (mapRef.current?.getSource("airports") as GeoJSONSource | undefined) : undefined;
    source?.setData((airports ?? EMPTY) as never);
  }, [ready, airports]);

  useEffect(() => {
    const source = ready ? (mapRef.current?.getSource("sigmets") as GeoJSONSource | undefined) : undefined;
    source?.setData((sigmets ?? EMPTY) as never);
  }, [ready, sigmets]);

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

  useEffect(() => {
    const map = mapRef.current;
    if (!ready || !map) return;
    const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    for (const id of ["field", "streamlines"]) map.setLayoutProperty(id, "visibility", mode3d ? "none" : "visible");
    if (mode3d) {
      map.dragRotate.enable();
      map.touchZoomRotate.enableRotation();
      map.easeTo({ pitch: 55, bearing: -15, duration: reduce ? 0 : 600 });
    } else {
      map.dragRotate.disable();
      map.touchZoomRotate.disableRotation();
      map.easeTo({ pitch: 0, bearing: 0, duration: reduce ? 0 : 400 });
    }
  }, [ready, mode3d]);

  const e = field ? gridEdges(field) : undefined;
  return (
    <div className="map-view">
      <div ref={container} className="map-canvas" role="application" tabIndex={0}
           aria-label={`Carte ${def.label}${e ? `, domaine ${e.south.toFixed(1)}–${e.north.toFixed(1)}° N` : ""}. Cliquer pour inspecter un point.`} />
    </div>
  );
}
