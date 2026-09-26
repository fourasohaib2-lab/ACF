/**
 * 3-D volume overlay (spec SP2B): deck.gl drawn over the MapLibre map with the same camera. MapLibre 6 is
 * not supported by deck.gl's interleaved mode (measured: runtime error), so the overlay has its own canvas.
 * Loaded lazily on the first switch to 3-D.
 */
import { MapboxOverlay } from "@deck.gl/mapbox";
import { ColumnLayer, PathLayer, TextLayer } from "@deck.gl/layers";
import type { Layer, PickingInfo } from "@deck.gl/core";
import type { IControl, Map as MlMap } from "maplibre-gl";
import { useEffect, useMemo, useRef } from "react";
import type { FieldData } from "../api/types";
import { bandVertices, buildVoxels, splitByBand, terrainVoxels, type Band, type Volume, type Voxels } from "./geometry";
import { classifier, type VolumeLayerDef } from "./layers3d";

const BAND_DEG = 2;
/** Levels labelled on the vertical scale (all 12 overlap in the lower layers). */
const SCALE_LEVELS = [850, 700, 500, 300, 200, 100];
const GENUS = ["Ci", "Cc", "Cs", "Ac", "As", "Ns", "Sc", "St", "Cu", "Cb"];

export interface VolumeInput { def: VolumeLayerDef; volume: Volume; aux?: Volume }
interface Props {
  map: MlMap;
  inputs: VolumeInput[];
  terrain: FieldData | undefined;
  exaggeration: number;
  threshold: number;
  awciBounds: number[];
  flightLevels: Record<number, number>; // hPa -> FL of the run
  onPickVoxel: (lat: number, lon: number, levelHpa: number) => void;
}
interface Picked { def?: VolumeLayerDef; volume?: Volume; aux?: Volume; voxels: Voxels; band: Band }

function columnLayers(id: string, voxels: Voxels, dLat: number, dLon: number, exaggeration: number, pickable: boolean,
                      registry: Map<string, Picked>, extra: Omit<Picked, "voxels" | "band">): Layer[] {
  return splitByBand(voxels, BAND_DEG).map((band) => {
    const layerId = `${id}-${band.lat}`;
    registry.set(layerId, { ...extra, voxels, band });
    return new ColumnLayer({
      id: layerId, data: { length: band.count, attributes: {
        getPosition: { value: band.positions, size: 3 }, getElevation: { value: band.thickness, size: 1 },
        getFillColor: { value: band.colors, size: 4, normalized: true } } } as never,
      diskResolution: 4, vertices: bandVertices(band.lat, dLat, dLon) as never, radius: 1, angle: 0, extruded: true,
      elevationScale: exaggeration, pickable, autoHighlight: pickable, highlightColor: [255, 255, 255, 90],
    });
  });
}

function scaleLayers(inputs: VolumeInput[], exaggeration: number, flightLevels: Record<number, number>): Layer[] {
  const v = inputs[0]?.volume;
  if (!v) return [];
  const n = v.ny * v.nx;
  // south edge, near the default camera (looking north), slightly inside the domain
  const lon = Math.min(v.lon0, v.lon1) + 0.1 * Math.abs(v.lon1 - v.lon0);
  const lat = Math.min(v.lat0, v.lat1) - 0.25;
  const ticks = v.levels.flatMap((hpa, k) => {
    if (!SCALE_LEVELS.includes(hpa)) return [];
    let sum = 0, cnt = 0;
    for (let c = 0; c < n; c++) { const z = v.gh[k * n + c]!; if (Number.isFinite(z)) { sum += z; cnt++; } }
    const km = cnt ? sum / cnt / 1000 : 0;
    const fl = flightLevels[hpa];
    return [{ position: [lon, lat, km * 1000 * exaggeration] as [number, number, number],
      text: `${hpa} hPa${fl !== undefined ? ` · FL${String(fl).padStart(3, "0")}` : ""} · ${km.toFixed(1).replace(".", ",")} km` }];
  });
  const top = Math.max(...ticks.map((t) => t.position[2]));
  return [
    new PathLayer({ id: "scale-axis", data: [{ path: [[lon, lat, 0], [lon, lat, top]] }], getPath: (d: { path: number[][] }) => d.path as never,
      getColor: [230, 236, 245, 220], widthUnits: "pixels", getWidth: 2, parameters: { depthCompare: "always" } }),
    new TextLayer({ id: "scale-labels", data: ticks, getPosition: (d) => d.position, getText: (d) => d.text, getSize: 12,
      getColor: [230, 236, 245, 255], getTextAnchor: "start", getAlignmentBaseline: "center", getPixelOffset: [8, 0],
      background: true, getBackgroundColor: [11, 18, 32, 200], fontFamily: "system-ui, sans-serif",
      parameters: { depthCompare: "always" } }), // the scale stays readable in front of the voxels
  ];
}

export function Volume3D({ map, inputs, terrain, exaggeration, threshold, awciBounds, flightLevels, onPickVoxel }: Props) {
  const overlay = useRef<MapboxOverlay | null>(null);
  const registry = useRef(new Map<string, Picked>());
  const pickRef = useRef(onPickVoxel);
  useEffect(() => { pickRef.current = onPickVoxel; }, [onPickVoxel]);

  useEffect(() => {
    const o = new MapboxOverlay({
      interleaved: false, layers: [],
      getTooltip: (info: PickingInfo) => {
        const p = info.layer ? registry.current.get(info.layer.id) : undefined;
        if (!p?.def || !p.volume || info.index < 0) return null;
        const g = p.band.index[info.index]!;
        const k = p.voxels.level[g]!;
        const i = k * p.volume.ny * p.volume.nx + p.voxels.cell[g]!;
        const value = p.volume.values[i]!;
        const genus = p.aux ? GENUS[p.aux.values[i]!] : undefined;
        const detail = p.def.id === "clouds" ? `${genus ?? ""} · fraction ${(value * 8).toFixed(1).replace(".", ",")} octas` : `valeur ${value.toFixed(1).replace(".", ",")}`;
        return { text: `${p.def.label} · ${p.volume.levels[k]} hPa · ${detail}` };
      },
      onClick: (info: PickingInfo) => {
        const p = info.layer ? registry.current.get(info.layer.id) : undefined;
        if (!p?.volume || info.index < 0) return;
        const g = p.band.index[info.index]!;
        pickRef.current(p.voxels.positions[g * 3 + 1]!, p.voxels.positions[g * 3]!, p.volume.levels[p.voxels.level[g]!]!);
      },
    });
    map.addControl(o as unknown as IControl);
    overlay.current = o;
    return () => { map.removeControl(o as unknown as IControl); overlay.current = null; };
  }, [map]);

  const scene = useMemo(() => {
    const reg = new Map<string, Picked>();
    const out: Layer[] = [];
    if (terrain) {
      const dLat = terrain.ny > 1 ? (terrain.lat1 - terrain.lat0) / (terrain.ny - 1) : 0.25;
      const dLon = terrain.nx > 1 ? (terrain.lon1 - terrain.lon0) / (terrain.nx - 1) : 0.25;
      out.push(...columnLayers("terrain", terrainVoxels(terrain), dLat, dLon, exaggeration, false, reg, {}));
    }
    const terrainAtVolume = (v: Volume) =>
      terrain && terrain.ny === v.ny && terrain.nx === v.nx ? terrain.values : new Float32Array(v.ny * v.nx);
    for (const { def, volume, aux } of inputs) {
      const classify = classifier(def, { threshold, awciBounds, aux: aux?.values });
      const voxels = buildVoxels(volume, terrainAtVolume(volume), classify, def.palette, exaggeration);
      const dLat = volume.ny > 1 ? (volume.lat1 - volume.lat0) / (volume.ny - 1) : 0.25;
      const dLon = volume.nx > 1 ? (volume.lon1 - volume.lon0) / (volume.nx - 1) : 0.25;
      out.push(...columnLayers(def.id, voxels, dLat, dLon, exaggeration, true, reg, { def, volume, aux }));
    }
    out.push(...scaleLayers(inputs, exaggeration, flightLevels));
    return { layers: out, reg };
  }, [inputs, terrain, exaggeration, threshold, awciBounds, flightLevels]);

  useEffect(() => {
    registry.current = scene.reg; // picking reads the voxels of the layers on screen
    overlay.current?.setProps({ layers: scene.layers });
  }, [scene]);
  return null;
}

export default Volume3D;
