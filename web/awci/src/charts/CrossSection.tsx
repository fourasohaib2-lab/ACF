import { useMemo, useState, type MouseEvent } from "react";
import type { RouteSection } from "../api/types";
import { fmt } from "../lib/format";
import { NM_PER_KM } from "../lib/route";
import { colorFn, type LayerDef } from "../map/layers";
import { DataTable } from "./DataTable";

interface Props {
  section: RouteSection;
  def: LayerDef;
  awciBounds: number[];
  classLabels: string[];
  /** Level on the map (hPa): marked across the section. */
  currentLevel: number;
  waypointLabels: string[];
  stale?: boolean;
}

const W = 960;
const H = 320;
const PAD = { l: 64, r: 56, t: 22, b: 36 };
const PLOT_W = W - PAD.l - PAD.r;
const PLOT_H = H - PAD.t - PAD.b;

/** Pressure interfaces of the level bands: geometric means of neighbours (midpoints in log p), mirrored at the ends. */
export function pressureBands(levels: number[]): { top: number; bottom: number }[] {
  const sorted = levels.map((p, i) => ({ p, i })).sort((a, b) => a.p - b.p); // top (low p) first
  const out: { top: number; bottom: number }[] = new Array(levels.length);
  sorted.forEach(({ p, i }, k) => {
    const up = sorted[k - 1]?.p;
    const down = sorted[k + 1]?.p;
    const top = up !== undefined ? Math.sqrt(up * p) : (p * p) / Math.sqrt(p * down!);
    const bottom = down !== undefined ? Math.sqrt(p * down) : (p * p) / Math.sqrt(p * up!);
    out[i] = { top, bottom };
  });
  return out;
}

export function valueText(def: LayerDef, v: number | null, classLabels: string[], awciBounds: number[]): string {
  if (v === null) return "sans donnée";
  const r = def.render;
  if (r.kind === "awci") return `${fmt(v, 0)} (${classLabels[awciBounds.filter((b) => v >= b).length] ?? ""})`;
  if (r.kind === "codes") return r.labels[Math.round(v)] ?? String(v);
  if (r.kind === "continuous") return `${fmt(v * (r.scale ?? 1), 1)} ${def.unit}`;
  return String(v);
}

const niceStep = (length: number) => [25, 50, 100, 200, 250, 500, 1000, 2000].find((s) => length / s <= 8) ?? 2500;

/**
 * Vertical cross-section along the route: distance (x) against pressure on a log scale (y), graduated in ISA
 * flight levels. Each sample is its nearest grid cell (no interpolation); the model relief (surface pressure)
 * hides the levels below it; a band without value above the relief is hatched as no data.
 */
export function CrossSection({ section: s, def, awciBounds, classLabels, currentLevel, waypointLabels, stale = false }: Props) {
  const [hover, setHover] = useState<{ k: number; li: number } | null>(null);
  const bands = useMemo(() => pressureBands(s.levels_hpa), [s.levels_hpa]);
  const sp = s.surface_pressure_hpa;
  const pTop = Math.min(...bands.map((b) => b.top));
  const pBottom = Math.max(...bands.map((b) => b.bottom), ...(sp ?? []).filter((v): v is number => v !== null));
  const y = (p: number) => PAD.t + ((Math.log(p) - Math.log(pTop)) / (Math.log(pBottom) - Math.log(pTop))) * PLOT_H;
  const L = s.length_km || 1;
  const x = (d: number) => PAD.l + (d / L) * PLOT_W;
  const n = s.distance_km.length;
  const edges = useMemo(() => s.distance_km.map((d, k): [number, number] => [
    k === 0 ? 0 : (s.distance_km[k - 1]! + d) / 2, k === n - 1 ? L : (d + s.distance_km[k + 1]!) / 2]), [s.distance_km, n, L]);
  const color = useMemo(() => colorFn(def, awciBounds), [def, awciBounds]);

  const cells = useMemo(() => {
    const out: { key: string; x0: number; x1: number; li: number; fill: string }[] = [];
    s.values.forEach((row, li) => {
      let run: { x0: number; x1: number; fill: string } | null = null;
      const flush = () => { if (run) out.push({ key: `${li}-${run.x0}`, li, ...run }); run = null; };
      row.forEach((v, k) => {
        const below = sp?.[k] != null && s.levels_hpa[li]! > sp[k]!;
        let fill: string | null;
        if (v === null) fill = below ? null : "url(#xs-hatch)";
        else { const c = color(v); fill = c ? `rgb(${c[0]},${c[1]},${c[2]})` : null; }
        const [a, b] = edges[k]!;
        if (fill && run && run.fill === fill && Math.abs(run.x1 - a) < 1e-9) run.x1 = b;
        else { flush(); if (fill) run = { x0: a, x1: b, fill }; }
      });
      flush();
    });
    return out;
  }, [s.values, s.levels_hpa, sp, edges, color]);

  const terrain = useMemo(() => {
    if (!sp) return null;
    const pts = sp.map((p, k) => (p === null ? null : `${x(s.distance_km[k]!).toFixed(1)},${y(p).toFixed(1)}`)).filter(Boolean);
    return pts.length ? `M${x(0).toFixed(1)},${(PAD.t + PLOT_H).toFixed(1)} L${pts.join(" L")} L${x(L).toFixed(1)},${(PAD.t + PLOT_H).toFixed(1)} Z` : null;
  }, [sp, s.distance_km, L]); // eslint-disable-line react-hooks/exhaustive-deps

  const onMove = (e: MouseEvent<SVGSVGElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    const px = ((e.clientX - r.left) / r.width) * W;
    const py = ((e.clientY - r.top) / r.height) * H;
    if (px < PAD.l || px > W - PAD.r || py < PAD.t || py > PAD.t + PLOT_H) { setHover(null); return; }
    const d = ((px - PAD.l) / PLOT_W) * L;
    let k = 0;
    while (k < n - 1 && edges[k]![1] < d) k++;
    const li = bands.findIndex((b) => py >= y(b.top) && py <= y(b.bottom));
    setHover(li >= 0 ? { k, li } : null);
  };

  // level labels at least 12 px apart (log p crowds the lowest levels); the current level is always labelled
  const labelled = useMemo(() => {
    const order = s.levels_hpa.map((p, li) => ({ p, li })).sort((a, b) => a.p - b.p);
    const out: number[] = [];
    let last = -Infinity;
    for (const { p, li } of order) {
      const yy = y(p);
      if (yy - last >= 12 || p === currentLevel) { out.push(li); last = yy; }
    }
    return out;
  }, [s.levels_hpa, currentLevel, pTop, pBottom]); // eslint-disable-line react-hooks/exhaustive-deps
  const step = niceStep(L);
  const ticks = Array.from({ length: Math.floor(L / step) + 1 }, (_, i) => i * step);
  const hv = hover ? s.values[hover.li]![hover.k]! : null;
  const hoverBelow = hover && sp?.[hover.k] != null && s.levels_hpa[hover.li]! > sp[hover.k]!;
  const perLevel = s.levels_hpa.map((p, li) => {
    let best: number | null = null;
    let at = -1;
    s.values[li]!.forEach((v, k) => { if (v !== null && (best === null || v > best)) { best = v; at = k; } });
    return [`FL${String(s.flight_levels[li]).padStart(3, "0")} (${p} hPa)`, valueText(def, best, classLabels, awciBounds),
      at >= 0 ? `${fmt(s.distance_km[at]!, 0)} km` : "—", s.values[li]!.filter((v) => v !== null).length];
  });

  return (
    <figure className={`chart cross-section${stale ? " is-stale" : ""}`}>
      <svg viewBox={`0 0 ${W} ${H}`} className="chart-svg" role="img" onMouseMove={onMove} onMouseLeave={() => setHover(null)}
           aria-label={`Coupe verticale de ${def.label} le long de la route, ${fmt(L, 0)} km, de FL${String(Math.min(...s.flight_levels)).padStart(3, "0")} à FL${String(Math.max(...s.flight_levels)).padStart(3, "0")}.`}>
        <defs>
          <pattern id="xs-hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <rect width="6" height="6" className="xs-nodata-bg" /><line x1="0" y1="0" x2="0" y2="6" className="xs-nodata-line" />
          </pattern>
        </defs>
        <rect x={PAD.l} y={PAD.t} width={PLOT_W} height={PLOT_H} className="xs-sky" />
        {cells.map((c) => (
          <rect key={c.key} x={x(c.x0)} width={Math.max(0.5, x(c.x1) - x(c.x0))} y={y(bands[c.li]!.top)}
                height={y(bands[c.li]!.bottom) - y(bands[c.li]!.top)} fill={c.fill} />
        ))}
        {terrain && <path d={terrain} className="xs-terrain"><title>Relief du modèle IFS (pression de surface)</title></path>}
        {labelled.map((li) => (
          <g key={s.levels_hpa[li]}>
            <text x={PAD.l - 6} y={y(s.levels_hpa[li]!) + 4} textAnchor="end" className="chart-tick">FL{String(s.flight_levels[li]).padStart(3, "0")}</text>
            <text x={W - PAD.r + 6} y={y(s.levels_hpa[li]!) + 4} className="chart-tick">{s.levels_hpa[li]}</text>
          </g>
        ))}
        <text x={W - PAD.r + 6} y={PAD.t - 8} className="chart-tick">hPa</text>
        <line x1={PAD.l} x2={W - PAD.r} y1={y(currentLevel)} y2={y(currentLevel)} className="xs-level" />
        {ticks.map((t) => (
          <g key={t}>
            <line x1={x(t)} x2={x(t)} y1={PAD.t + PLOT_H} y2={PAD.t + PLOT_H + 4} className="chart-grid" />
            <text x={x(t)} y={PAD.t + PLOT_H + 16} textAnchor="middle" className="chart-tick">{t}</text>
          </g>
        ))}
        <text x={W - PAD.r} y={H - 4} textAnchor="end" className="chart-tick">km</text>
        {s.waypoints.map((w, i) => (
          <g key={w.index}>
            <line x1={x(w.distance_km)} x2={x(w.distance_km)} y1={PAD.t} y2={PAD.t + PLOT_H} className="xs-waypoint" />
            <text x={x(w.distance_km)} y={PAD.t - 8} textAnchor={i === 0 ? "start" : i === s.waypoints.length - 1 ? "end" : "middle"}
                  className="xs-waypoint-label">{waypointLabels[i] ?? `P${i + 1}`}</text>
          </g>
        ))}
        {hover && (
          <rect x={x(edges[hover.k]![0])} width={Math.max(1, x(edges[hover.k]![1]) - x(edges[hover.k]![0]))}
                y={y(bands[hover.li]!.top)} height={y(bands[hover.li]!.bottom) - y(bands[hover.li]!.top)} className="xs-hover" />
        )}
      </svg>
      {hover ? (
        <div className="xs-readout" role="status">
          <strong>{fmt(s.distance_km[hover.k]!, 0)} km ({fmt(s.distance_km[hover.k]! * NM_PER_KM, 0)} NM) ·
            FL{String(s.flight_levels[hover.li]).padStart(3, "0")} ({s.levels_hpa[hover.li]} hPa)</strong>
          <span>{hoverBelow ? "Sous le relief du modèle" : `${def.label} : ${valueText(def, hv, classLabels, awciBounds)}`}</span>
          <span className="num">Maille {fmt(s.grid_lat[hover.k]!, 2)}° N, {fmt(s.grid_lon[hover.k]!, 2)}° E</span>
        </div>
      ) : <div className="xs-readout xs-readout-hint">Survoler la coupe pour lire une valeur.</div>}
      <figcaption className="chart-legend">
        <span><i className="xs-key-terrain" />relief du modèle</span>
        <span><i className="xs-key-nodata" />sans donnée</span>
        <span><i className="xs-key-level" />niveau de la carte</span>
        <span>Longueur {fmt(L, 0)} km ({fmt(L * NM_PER_KM, 0)} NM), maille la plus proche tous les {s.spacing_km} km, sans interpolation</span>
      </figcaption>
      <details className="chart-data">
        <summary>Voir les données</summary>
        <DataTable caption={`Coupe verticale : ${def.label}, maximum par niveau le long de la route`}
                   columns={["Niveau", "Maximum", "À", "Échantillons avec valeur"]} rows={perLevel} />
      </details>
    </figure>
  );
}
