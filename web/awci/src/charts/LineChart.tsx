import { useMemo, useState, type MouseEvent } from "react";
import { DataTable } from "./DataTable";

export interface Series { id: string; label: string; color: string; points: { x: number; y: number | null }[] }
interface Props {
  series: Series[];
  yLabel: string;
  format: (v: number) => string;
  xFormat?: (x: number) => string;
  xCurrent?: number;
  yDomain?: [number, number];
  height?: number;
}

const W = 380; // close to the rendered width, so 11 px ticks stay 11 px
const PAD = { l: 44, r: 12, t: 10, b: 24 };

/** One-axis line chart (dataviz rules): thin lines, hover crosshair + tooltip, legend from 2 series, data table. */
export function LineChart({ series, yLabel, format, xFormat = (x) => String(x), xCurrent, yDomain, height = 180 }: Props) {
  const [hover, setHover] = useState<number | null>(null);
  const xs = useMemo(() => [...new Set(series.flatMap((s) => s.points.map((p) => p.x)))].sort((a, b) => a - b), [series]);
  const ys = series.flatMap((s) => s.points.map((p) => p.y)).filter((y): y is number => y !== null);
  const [y0, y1] = yDomain ?? [Math.min(0, ...ys), Math.max(1, ...ys)];
  const x0 = xs[0] ?? 0;
  const x1 = xs[xs.length - 1] ?? 1;
  const sx = (x: number) => PAD.l + ((x - x0) / (x1 - x0 || 1)) * (W - PAD.l - PAD.r);
  const sy = (y: number) => PAD.t + (1 - (y - y0) / (y1 - y0 || 1)) * (height - PAD.t - PAD.b);
  const ticks = [y0, (y0 + y1) / 2, y1];

  const path = (s: Series) => {
    let d = "";
    let pen = false;
    for (const p of [...s.points].sort((a, b) => a.x - b.x)) {
      if (p.y === null) { pen = false; continue; } // a gap stays a gap: missing values are not interpolated
      d += `${pen ? "L" : "M"}${sx(p.x).toFixed(1)},${sy(p.y).toFixed(1)}`;
      pen = true;
    }
    return d;
  };
  const onMove = (e: MouseEvent<SVGSVGElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * W;
    let best: number | null = null;
    for (const v of xs) if (best === null || Math.abs(sx(v) - x) < Math.abs(sx(best) - x)) best = v;
    setHover(best);
  };
  const valueAt = (s: Series, x: number) => s.points.find((p) => p.x === x)?.y ?? null;

  return (
    <figure className="chart">
      <svg viewBox={`0 0 ${W} ${height}`} className="chart-svg" role="img" aria-label={`${yLabel} : ${series.map((s) => s.label).join(", ")}`}
           onMouseMove={onMove} onMouseLeave={() => setHover(null)}>
        {ticks.map((t) => (
          <g key={t}>
            <line x1={PAD.l} x2={W - PAD.r} y1={sy(t)} y2={sy(t)} className="chart-grid" />
            <text x={PAD.l - 6} y={sy(t) + 4} textAnchor="end" className="chart-tick">{format(t)}</text>
          </g>
        ))}
        {xs.length > 1 && [xs[0]!, xs[xs.length - 1]!].map((x, i) => (
          <text key={x} x={sx(x)} y={height - 6} textAnchor={i ? "end" : "start"} className="chart-tick">{xFormat(x)}</text>
        ))}
        {xCurrent !== undefined && <line x1={sx(xCurrent)} x2={sx(xCurrent)} y1={PAD.t} y2={height - PAD.b} className="chart-current" />}
        {series.map((s) => <path key={s.id} d={path(s)} fill="none" stroke={s.color} strokeWidth={1.6} />)}
        {series.flatMap((s) => s.points.filter((p) => p.y !== null).map((p) =>
          <circle key={`${s.id}-${p.x}`} cx={sx(p.x)} cy={sy(p.y!)} r={2} fill={s.color} />))}
        {hover !== null && <line x1={sx(hover)} x2={sx(hover)} y1={PAD.t} y2={height - PAD.b} className="chart-crosshair" />}
      </svg>
      {hover !== null && (
        <div className="chart-tooltip" role="status">
          <strong>{xFormat(hover)}</strong>
          {series.map((s) => { const v = valueAt(s, hover); return <span key={s.id}><i style={{ background: s.color }} />{s.label} : {v === null ? "—" : format(v)}</span>; })}
        </div>
      )}
      {series.length >= 2 && (
        <figcaption className="chart-legend">{series.map((s) => <span key={s.id}><i style={{ background: s.color }} />{s.label}</span>)}</figcaption>
      )}
      <details className="chart-data">
        <summary>Voir les données</summary>
        <DataTable caption={yLabel} columns={["Instant", ...series.map((s) => s.label)]}
                   rows={xs.map((x) => [xFormat(x), ...series.map((s) => { const v = valueAt(s, x); return v === null ? "—" : format(v); })])} />
      </details>
    </figure>
  );
}
